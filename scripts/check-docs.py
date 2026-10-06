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
extractor nor listed in REPOSITORY_FILES or PENDING_FILES.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
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

# Tracked files that a later ticket's extractor will account for. Each ticket
# deletes its group once its extractor reads these files. Exact paths only, one
# per line, so unrelated additions still fail.
PENDING_FILES = [
    # Unused and awaiting deletion; remove this line in the same change that
    # deletes the file
    "bin/executable_md-to-gmail.sh",

    # Config files (PER-98)
    ".chezmoi.toml.tmpl",
    "dot_gitconfig",
    "dot_nirc",
    "dot_zprofile",
    "dot_zshenv",
    "dot_zshrc",
    "private_dot_codex/AGENTS.md",
    "private_dot_config/gh/private_config.yml",
    "private_dot_config/ghostty/config.ghostty",
    "private_dot_config/linearmouse/linearmouse.json",
    "private_dot_config/mise/config.toml",
    "private_dot_config/private_karabiner/private_karabiner.json",

    # Global Node packages (PER-98)
    ".chezmoidata/packages.toml",

    # Fonts (PER-98)
    "fonts/MonoLisaVariableItalic.ttf",
    "fonts/MonoLisaVariableNormal.ttf",

    # Chezmoi run files (PER-98)
    "run_once_install-fonts.sh",
    "run_once_install-latex-pandoc.sh",
    "run_once_macos-defaults.sh",
    "run_onchange_after_10-macos-keyboard.sh.tmpl",
    "run_onchange_after_20-macos-finder.sh.tmpl",
    "run_onchange_after_30-install-packages.sh.tmpl",
    "run_onchange_after_40-install-pre-commit-hook.sh.tmpl",
]


@dataclass(frozen=True)
class Coverage:
    """What one extractor found: items that need entries in one doc."""

    kind: str  # Singular noun used in messages, e.g. "Homebrew formula".
    doc: str  # Repository path of the doc that must have an entry per item.
    items: frozenset[str]
    files: frozenset[str]  # Tracked files this extractor accounts for.


Extractor = Callable[[Path], Coverage]
EXTRACTORS: list[Extractor] = []


def extractor(function: Extractor) -> Extractor:
    """Register an extractor. Add new categories with this decorator."""
    EXTRACTORS.append(function)
    return function


DocParser = Callable[[str], set[str]]
DOC_PARSERS: dict[str, DocParser] = {}

# Template comments and code samples hold example entries, not real ones.
NOT_ENTRIES = re.compile(r"<!--.*?-->|^```.*?^```", re.DOTALL | re.MULTILINE)


def doc_parser(doc: str) -> Callable[[DocParser], DocParser]:
    """Register the function that lists the entry names in a doc.

    The function receives the doc without HTML comments and fenced code blocks.
    """

    def register(function: DocParser) -> DocParser:
        DOC_PARSERS[doc] = function
        return function

    return register


# ─── Doc parsers ──────────────────────────────────────────────────────────

INVENTORY_ENTRY = re.compile(r"^\s*[-*]\s+\*\*\[([^\]]+)\]\([^)]*\)\*\*", re.MULTILINE)


@doc_parser(INVENTORY)
def inventory_entries(text: str) -> set[str]:
    """Entries are bullets that start with a bold, linked name."""
    return {name.strip("`") for name in INVENTORY_ENTRY.findall(text)}


# ─── Inventory extractors ─────────────────────────────────────────────────

BREWFILE = "dot_Brewfile"


def brewfile_entries(root: Path, entry_type: str) -> set[str]:
    """Names from Brewfile lines such as `brew "owner/tap/name"`, without the tap."""
    pattern = re.compile(rf"""^\s*{entry_type}\s+["']([^"']+)["']""", re.MULTILINE)
    return {name.rsplit("/", 1)[-1] for name in pattern.findall(read(root, BREWFILE))}


@extractor
def homebrew_formulae(root: Path) -> Coverage:
    return Coverage(
        kind="Homebrew formula",
        doc=INVENTORY,
        items=frozenset(brewfile_entries(root, "brew")),
        files=frozenset({BREWFILE}),
    )


# ─── Usage guide extractors ───────────────────────────────────────────────


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
        documented: set[str] = set()
        for coverage in (c for c in coverages if c.doc == doc):
            documented |= coverage.items
            for item in sorted(coverage.items - entries):
                errors.append(f"{doc}: missing an entry for {coverage.kind} '{item}'")
        for entry in sorted(entries - documented):
            errors.append(
                f"{doc}: entry '{entry}' matches nothing in the repository; "
                "remove it, or teach scripts/check-docs.py to extract it"
            )

    accounted = set().union(*(coverage.files for coverage in coverages))
    listed = REPOSITORY_FILES + PENDING_FILES
    for path in tracked_files(root):
        if path not in accounted and not any(fnmatch(path, p) for p in listed):
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
