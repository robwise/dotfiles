# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Check that the docs cover everything the repository sets up.

Run with: uv run scripts/check-docs.py

Each extractor reads repository files directly and returns a Coverage: the doc
that must document its items, the item names, and the tracked files it reads.
The check fails when an item has no entry in its doc, when a doc has an entry
that no extractor produced, or when a tracked file is neither read by an
extractor nor listed in REPOSITORY_FILES.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tomllib
from collections.abc import Callable
from dataclasses import dataclass
from fnmatch import fnmatch
from pathlib import Path

INVENTORY = "docs/inventory.md"
USAGE = "docs/usage.md"

# Tracked files that describe or check the repository rather than set up the
# machine. Patterns use fnmatch syntax.
REPOSITORY_FILES = [
    ".chezmoiignore",
    ".github/workflows/check-docs.yml",
    ".gitignore",
    ".pre-commit-config.yaml",
    "AGENTS.md",
    "GLOSSARY.md",
    "README.md",
    "docs/*",
    "scripts/check-docs.py",
    "scripts/test_check_docs.py",
]


@dataclass(frozen=True)
class Entry:
    """A name a doc documents, and the header of the table it sits in, if any."""

    name: str
    table: str = ""


@dataclass(frozen=True)
class Coverage:
    """What one extractor found: items that need entries in one doc."""

    kind: str  # Singular noun used in messages, e.g. "Homebrew formula".
    doc: str  # Repository path of the doc that must have an entry per item.
    items: frozenset[str]
    files: frozenset[str]  # Tracked files this extractor accounts for.
    # Header of the doc tables whose entries count, e.g. "Key | Does"; None
    # counts entries anywhere in the doc.
    table: str | None = None

    def accepts(self, entry: Entry) -> bool:
        return self.table is None or self.table == entry.table


Extractor = Callable[[Path], Coverage]
EXTRACTORS: list[Extractor] = []


def extractor(function: Extractor) -> Extractor:
    """Register an extractor. Add new categories with this decorator."""
    EXTRACTORS.append(function)
    return function


DocParser = Callable[[str], set[Entry]]
DOC_PARSERS: dict[str, DocParser] = {}

# Template comments and code samples hold example entries, not real ones.
NOT_ENTRIES = re.compile(r"<!--.*?-->|^```.*?^```", re.DOTALL | re.MULTILINE)


def doc_parser(doc: str) -> Callable[[DocParser], DocParser]:
    """Register the function that lists the entries in a doc.

    The function receives the doc without HTML comments and fenced code blocks.
    """

    def register(function: DocParser) -> DocParser:
        DOC_PARSERS[doc] = function
        return function

    return register


# ─── Doc parsers ──────────────────────────────────────────────────────────

INVENTORY_ENTRY = re.compile(r"^\s*[-*]\s+\*\*\[([^\]]+)\]\([^)]*\)\*\*", re.MULTILINE)


@doc_parser(INVENTORY)
def inventory_entries(text: str) -> set[Entry]:
    """Entries are bullets that start with a bold, linked name, under any heading."""
    return {Entry(name.strip("`")) for name in INVENTORY_ENTRY.findall(text)}


TABLE_ROW = re.compile(r"^\s*\|")
CODE_SPAN = re.compile(r"`([^`\n]+)`")


def table_cells(row: str) -> list[str]:
    return [cell.strip() for cell in row.strip().strip("|").split("|")]


@doc_parser(USAGE)
def usage_entries(text: str) -> set[Entry]:
    """Entries are code spans in the first cell of a table's body rows.

    Each entry records its table's header row, such as "Key | Does", so a
    category can count only the tables meant for it. Code spans elsewhere in a
    row, in header rows, in prose, or in lists are not entries.
    """
    entries: set[Entry] = set()
    header = None
    for line in text.splitlines():
        if not TABLE_ROW.match(line):
            header = None
        elif header is None:
            header = " | ".join(table_cells(line))
        else:
            first_cell = table_cells(line)[0]
            entries |= {Entry(name.strip(), header) for name in CODE_SPAN.findall(first_cell)}
    return entries


# ─── Inventory extractors ─────────────────────────────────────────────────

BREWFILE = "dot_Brewfile"


def brewfile_entries(root: Path, entry_type: str) -> set[str]:
    """Names from Brewfile lines such as `brew "owner/tap/name"`, without the tap."""
    pattern = re.compile(rf"""^\s*{entry_type}\s+["']([^"']+)["']""", re.MULTILINE)
    return {name.rsplit("/", 1)[-1] for name in pattern.findall(read(root, BREWFILE))}


# Brewfile entry types where every entry is a Package of one kind. Casks are
# split between Homebrew casks and Fonts below.
BREWFILE_PACKAGES = {
    "brew": "Homebrew formula",
    "vscode": "VS Code extension",
    "uv": "Global Python package",
}


def brewfile_extractor(entry_type: str, kind: str) -> Extractor:
    def extract(root: Path) -> Coverage:
        return Coverage(
            kind=kind,
            doc=INVENTORY,
            items=frozenset(brewfile_entries(root, entry_type)),
            files=frozenset({BREWFILE}),
        )

    extract.__name__ = extract.__qualname__ = f"brewfile_{entry_type}_packages"
    return extract


for entry_type, kind in BREWFILE_PACKAGES.items():
    extractor(brewfile_extractor(entry_type, kind))


# Homebrew names every font cask `font-*`; those belong under Fonts.
FONT_CASK_PREFIX = "font-"


@extractor
def homebrew_casks(root: Path) -> Coverage:
    casks = brewfile_entries(root, "cask")
    return Coverage(
        kind="Homebrew cask",
        doc=INVENTORY,
        items=frozenset(c for c in casks if not c.startswith(FONT_CASK_PREFIX)),
        files=frozenset({BREWFILE}),
    )


# Source-state attribute prefixes chezmoi strips from each path component.
CHEZMOI_ATTRIBUTES = re.compile(
    r"^(?:encrypted_|private_|readonly_|empty_|executable_|exact_)*"
)
# The config template `chezmoi init` renders into chezmoi's own config file.
CHEZMOI_CONFIG_TEMPLATE = re.compile(r"^\.chezmoi\.(\w+)\.tmpl$")


def is_run_file(path: str) -> bool:
    """Whether chezmoi runs this source file instead of writing it."""
    return Path(path).name.startswith("run_")


def chezmoi_target(source: str) -> str:
    """The home-relative path chezmoi writes for a source path."""
    parts = []
    for part in source.split("/"):
        part = CHEZMOI_ATTRIBUTES.sub("", part)
        if part.startswith("dot_"):
            part = "." + part.removeprefix("dot_")
        parts.append(part)
    return "/".join(parts).removesuffix(".tmpl")


@extractor
def config_files(root: Path) -> Coverage:
    """Tracked files chezmoi writes to dotted paths in the home directory."""
    items: set[str] = set()
    files: set[str] = set()
    for path in tracked_files(root):
        if config := CHEZMOI_CONFIG_TEMPLATE.match(path):
            items.add(f"~/.config/chezmoi/chezmoi.{config[1]}")
            files.add(path)
            continue
        if path.startswith(".") or is_run_file(path):
            continue
        target = chezmoi_target(path)
        if target.startswith("."):
            items.add(f"~/{target}")
            files.add(path)
    return Coverage(
        kind="Config file",
        doc=INVENTORY,
        items=frozenset(items),
        files=frozenset(files),
    )


FONT_FILES = "fonts/*"


@extractor
def fonts(root: Path) -> Coverage:
    """Font casks from the Brewfile and font files kept in `fonts/`."""
    casks = brewfile_entries(root, "cask")
    font_files = {p for p in tracked_files(root) if fnmatch(p, FONT_FILES)}
    return Coverage(
        kind="Font",
        doc=INVENTORY,
        items=frozenset(
            {c for c in casks if c.startswith(FONT_CASK_PREFIX)}
            | {Path(p).name for p in font_files}
        ),
        files=frozenset({BREWFILE} | font_files),
    )


PACKAGES = ".chezmoidata/packages.toml"
# `name@version` or `@scope/name@version`; the entry is the name.
NODE_PACKAGE_SPEC = re.compile(r"^(@?[^@]+)(?:@.*)?$")


@extractor
def global_node_packages(root: Path) -> Coverage:
    specs = tomllib.loads(read(root, PACKAGES)).get("packages", {}).get("node", [])
    return Coverage(
        kind="Global Node package",
        doc=INVENTORY,
        items=frozenset(NODE_PACKAGE_SPEC.sub(r"\1", spec) for spec in specs),
        files=frozenset({PACKAGES}),
    )


MISE_CONFIG = "private_dot_config/mise/config.toml"


@extractor
def javascript_toolchain_packages(root: Path) -> Coverage:
    """The `[tools]` that mise installs: node and its package managers."""
    packages = tomllib.loads(read(root, MISE_CONFIG)).get("tools", {})
    return Coverage(
        kind="JavaScript toolchain package",
        doc=INVENTORY,
        items=frozenset(packages),
        files=frozenset({MISE_CONFIG}),
    )


@extractor
def chezmoi_run_files(root: Path) -> Coverage:
    run_files = {p for p in tracked_files(root) if is_run_file(p)}
    return Coverage(
        kind="Chezmoi run file",
        doc=INVENTORY,
        items=frozenset(Path(p).name for p in run_files),
        files=frozenset(run_files),
    )


# ─── Usage guide extractors ───────────────────────────────────────────────

# Every zsh startup file this repository manages.
ZSH_CONFIGS = frozenset({"dot_zshenv", "dot_zprofile", "dot_zshrc"})
SHELL_ALIAS = re.compile(r"^\s*alias\s+([^=\s]+)=", re.MULTILINE)


def read_zsh_configs(root: Path) -> str:
    return "\n".join(read(root, path) for path in sorted(ZSH_CONFIGS))


@extractor
def shell_aliases(root: Path) -> Coverage:
    return Coverage(
        kind="Shell alias",
        doc=USAGE,
        items=frozenset(SHELL_ALIAS.findall(read_zsh_configs(root))),
        files=ZSH_CONFIGS,
    )


GITCONFIG = "dot_gitconfig"
GIT_SECTION = re.compile(r"^\s*\[([^\]]+)\]")
GIT_KEY = re.compile(r"^\s*([A-Za-z0-9-]+)\s*=")


@extractor
def git_aliases(root: Path) -> Coverage:
    """Keys of every `[alias]` section, documented as `git <alias>`."""
    aliases: set[str] = set()
    section = ""
    for line in read(root, GITCONFIG).splitlines():
        if match := GIT_SECTION.match(line):
            section = match.group(1).strip().lower()
        elif section == "alias" and (match := GIT_KEY.match(line)):
            aliases.add(f"git {match.group(1)}")
    return Coverage(
        kind="Git alias",
        doc=USAGE,
        items=frozenset(aliases),
        files=frozenset({GITCONFIG}),
    )


GH_CONFIG = "private_dot_config/gh/private_config.yml"
GH_ALIASES_BLOCK = re.compile(r"^aliases:[ \t]*\n((?:[ \t]+.*\n?|[ \t]*\n)*)", re.MULTILINE)
GH_ALIAS = re.compile(r"""^[ \t]+["']?([^"':#\s]+)["']?[ \t]*:""", re.MULTILINE)


@extractor
def gh_aliases(root: Path) -> Coverage:
    """Keys of the top-level `aliases:` mapping, documented as `gh <alias>`."""
    block = GH_ALIASES_BLOCK.search(read(root, GH_CONFIG))
    aliases = GH_ALIAS.findall(block.group(1)) if block else []
    return Coverage(
        kind="gh alias",
        doc=USAGE,
        items=frozenset(f"gh {alias}" for alias in aliases),
        files=frozenset({GH_CONFIG}),
    )


# `name() {`, `function name() {`, or `function name {`.
SHELL_FUNCTION = re.compile(
    r"^\s*(?:function\s+([^\s(){}]+)(?:\s*\(\))?|([^\s(){}=]+)\s*\(\))\s*\{",
    re.MULTILINE,
)
# `zle -N widget [function]` registers a line editor widget, not a command.
ZLE_WIDGET = re.compile(r"^\s*zle\s+-N\s+(\S+)(?:[ \t]+([^\s#]\S*))?", re.MULTILINE)


@extractor
def shell_functions(root: Path) -> Coverage:
    """Zsh functions you type as commands; line editor widgets are skipped."""
    zsh = read_zsh_configs(root)
    functions = {a or b for a, b in SHELL_FUNCTION.findall(zsh)}
    widgets = {function or widget for widget, function in ZLE_WIDGET.findall(zsh)}
    return Coverage(
        kind="Alias (shell function)",
        doc=USAGE,
        items=frozenset(functions - widgets),
        files=ZSH_CONFIGS,
    )


KARABINER = "private_dot_config/private_karabiner/private_karabiner.json"
KEY_REMAP_TABLE = "Key | Does"


@extractor
def karabiner_rules(root: Path) -> Coverage:
    """Descriptions of the complex modification rules in every Karabiner profile."""
    text = read(root, KARABINER)
    profiles = json.loads(text).get("profiles", []) if text.strip() else []
    return Coverage(
        kind="Key remap",
        doc=USAGE,
        table=KEY_REMAP_TABLE,
        items=frozenset(
            rule["description"]
            for profile in profiles
            for rule in profile.get("complex_modifications", {}).get("rules", [])
            if rule.get("description")
        ),
        files=frozenset({KARABINER}),
    )


# ─── Check ────────────────────────────────────────────────────────────────


def read(root: Path, path: str) -> str:
    file = root / path
    return file.read_text() if file.exists() else ""


def check(root: Path) -> list[str]:
    errors: list[str] = []
    coverages = [extract(root) for extract in EXTRACTORS]
    for coverage in coverages:
        if coverage.doc not in DOC_PARSERS:
            raise LookupError(f"no @doc_parser registered for {coverage.doc}")

    for doc, parse in DOC_PARSERS.items():
        entries = parse(NOT_ENTRIES.sub("", read(root, doc)))
        expected: set[str] = set()
        for coverage in (c for c in coverages if c.doc == doc):
            expected |= coverage.items
            found = {e.name for e in entries if coverage.accepts(e)}
            for item in sorted(coverage.items - found):
                errors.append(f"{doc}: missing an entry for {coverage.kind} '{item}'")
        for name in sorted({e.name for e in entries} - expected):
            errors.append(
                f"{doc}: entry '{name}' matches nothing in the repository; "
                "remove it, or teach scripts/check-docs.py to extract it"
            )

    accounted = set().union(*(coverage.files for coverage in coverages))
    for path in tracked_files(root):
        if path not in accounted and not any(
            fnmatch(path, pattern) for pattern in REPOSITORY_FILES
        ):
            errors.append(
                f"{path}: tracked file is not accounted for; teach "
                "scripts/check-docs.py to extract it, or add it to REPOSITORY_FILES"
            )

    return errors


def tracked_files(root: Path) -> list[str]:
    output = subprocess.run(
        ["git", "-C", str(root), "ls-files", "-z"],
        capture_output=True,
        check=True,
        text=True,
    ).stdout
    return sorted(path for path in output.split("\0") if path)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parent.parent,
        help="repository to check (default: this script's repository)",
    )
    root = parser.parse_args().root

    errors = check(root)
    for error in errors:
        print(error, file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
