"""Tests for scripts/check-docs.py.

Each test builds a fixture repository (a temporary git repository) and runs
the check against it through its command-line interface.

Run with: uv run python -m unittest discover -s scripts
"""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / "check-docs.py"

INVENTORY_HEADER = "# Inventory\n\n"

# dot_Brewfile is also a config file, so fixtures that write it need this entry.
BREWFILE_ENTRY = (
    "- **[`~/.Brewfile`](https://docs.brew.sh/Brew-Bundle-and-Brewfile)**: Brewfile.\n"
)


class FixtureRepo:
    """A temporary git repository whose tracked files the check reads."""

    def __init__(self, root: Path):
        self.root = root
        subprocess.run(["git", "init", "-q", str(root)], check=True)

    def write(self, path: str, text: str) -> None:
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text)
        self._git("add", "--", path)

    def remove(self, path: str) -> None:
        (self.root / path).unlink()
        self._git("add", "-A", "--", path)

    def check(self) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(SCRIPT), "--root", str(self.root)],
            capture_output=True,
            text=True,
        )

    def _git(self, *args: str) -> None:
        subprocess.run(["git", "-C", str(self.root), *args], check=True)


class CheckTestCase(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.repo = FixtureRepo(Path(tmp.name))

    def assertPasses(self):
        result = self.repo.check()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def assertFailsMentioning(self, *fragments: str):
        result = self.repo.check()
        output = result.stdout + result.stderr
        self.assertNotEqual(result.returncode, 0, output)
        for fragment in fragments:
            self.assertIn(fragment, output)


class HomebrewFormulaeTest(CheckTestCase):
    def setUp(self):
        super().setUp()
        self.repo.write("dot_Brewfile", 'tap "acme/tap"\nbrew "bat"\n')
        self.repo.write(
            "docs/inventory.md",
            INVENTORY_HEADER
            + BREWFILE_ENTRY
            + "## Homebrew formulae\n\n"
            + "- **[bat](https://github.com/sharkdp/bat)**: Pager.\n",
        )

    def test_passes_when_every_formula_has_an_inventory_entry(self):
        self.assertPasses()

    def test_fails_naming_a_formula_missing_from_the_inventory(self):
        self.repo.write("dot_Brewfile", 'brew "bat"\nbrew "jq"\n')
        self.assertFailsMentioning("Homebrew formula", "jq", "docs/inventory.md")

    def test_fails_naming_an_inventory_entry_for_a_removed_formula(self):
        self.repo.write("dot_Brewfile", 'tap "acme/tap"\n')
        self.assertFailsMentioning("bat", "docs/inventory.md")

    def test_ignores_example_entries_in_the_template_comment(self):
        self.repo.write(
            "docs/inventory.md",
            INVENTORY_HEADER
            + "<!--\nFormat:\n\n- **[node](https://nodejs.org)**: Runtime.\n-->\n\n"
            + BREWFILE_ENTRY
            + "- **[bat](https://github.com/sharkdp/bat)**: Pager.\n",
        )
        self.assertPasses()

    def test_documents_a_tapped_formula_by_its_short_name(self):
        self.repo.write("dot_Brewfile", 'brew "bat"\nbrew "acme/tap/gizmo"\n')
        self.assertFailsMentioning("'gizmo'")
        self.repo.write(
            "docs/inventory.md",
            INVENTORY_HEADER
            + BREWFILE_ENTRY
            + "- **[bat](https://github.com/sharkdp/bat)**: Pager.\n"
            + "- **[gizmo](https://example.com/gizmo)**: Widgets.\n",
        )
        self.assertPasses()

    def test_counts_only_bullets_that_start_with_a_bold_linked_name(self):
        self.repo.write(
            "docs/inventory.md",
            INVENTORY_HEADER
            + "## Homebrew formulae\n\n"
            + "- [bat](https://github.com/sharkdp/bat): Pager.\n"
            + "Uses **[bat](https://github.com/sharkdp/bat)** for previews.\n",
        )
        self.assertFailsMentioning("'bat'")


class HomebrewCasksTest(CheckTestCase):
    def setUp(self):
        super().setUp()
        self.repo.write("dot_Brewfile", 'cask "ghostty"\n')
        self.repo.write(
            "docs/inventory.md",
            INVENTORY_HEADER
            + BREWFILE_ENTRY
            + "## Homebrew casks\n\n"
            + "- **[ghostty](https://ghostty.org/)**: Terminal.\n",
        )

    def test_passes_when_every_cask_has_an_inventory_entry(self):
        self.assertPasses()

    def test_fails_naming_a_cask_missing_from_the_inventory(self):
        self.repo.write("dot_Brewfile", 'cask "ghostty"\ncask "cursor"\n')
        self.assertFailsMentioning("Homebrew cask", "'cursor'", "docs/inventory.md")

    def test_fails_naming_an_inventory_entry_for_a_removed_cask(self):
        self.repo.write("dot_Brewfile", "")
        self.assertFailsMentioning("'ghostty'", "docs/inventory.md")

    def test_leaves_font_casks_to_the_fonts_section(self):
        self.repo.write(
            "dot_Brewfile", 'cask "ghostty"\ncask "font-symbols-only-nerd-font"\n'
        )
        result = self.repo.check()
        self.assertNotIn("Homebrew cask 'font-symbols-only-nerd-font'", result.stderr)


class FontsTest(CheckTestCase):
    def setUp(self):
        super().setUp()
        self.repo.write("dot_Brewfile", 'cask "font-symbols-only-nerd-font"\n')
        self.repo.write("fonts/MonoLisaVariableNormal.ttf", "glyphs\n")
        self.repo.write(
            "docs/inventory.md",
            INVENTORY_HEADER
            + BREWFILE_ENTRY
            + "## Fonts\n\n"
            + "- **[font-symbols-only-nerd-font](https://github.com/ryanoasis/nerd-fonts)**: Icons.\n"
            + "- **[MonoLisaVariableNormal.ttf](https://www.monolisa.dev/)**: Coding font.\n",
        )

    def test_passes_when_every_font_has_an_inventory_entry(self):
        self.assertPasses()

    def test_fails_naming_a_font_cask_missing_from_the_inventory(self):
        self.repo.write(
            "dot_Brewfile",
            'cask "font-symbols-only-nerd-font"\ncask "font-fira-code"\n',
        )
        self.assertFailsMentioning("Font", "'font-fira-code'", "docs/inventory.md")

    def test_fails_naming_a_font_file_missing_from_the_inventory(self):
        self.repo.write("fonts/MonoLisaVariableItalic.ttf", "glyphs\n")
        self.assertFailsMentioning(
            "Font", "'MonoLisaVariableItalic.ttf'", "docs/inventory.md"
        )

    def test_fails_naming_an_inventory_entry_for_a_removed_font_file(self):
        self.repo.remove("fonts/MonoLisaVariableNormal.ttf")
        self.assertFailsMentioning("'MonoLisaVariableNormal.ttf'", "docs/inventory.md")

    def test_fails_naming_an_inventory_entry_for_a_removed_font_cask(self):
        self.repo.write("dot_Brewfile", "")
        self.assertFailsMentioning(
            "'font-symbols-only-nerd-font'", "docs/inventory.md"
        )


class VSCodeExtensionsTest(CheckTestCase):
    def setUp(self):
        super().setUp()
        self.repo.write("dot_Brewfile", 'vscode "eamodio.gitlens"\n')
        self.repo.write(
            "docs/inventory.md",
            INVENTORY_HEADER
            + BREWFILE_ENTRY
            + "## VS Code extensions\n\n"
            + "- **[eamodio.gitlens](https://marketplace.visualstudio.com/items?itemName=eamodio.gitlens)**: Blame.\n",
        )

    def test_passes_when_every_extension_has_an_inventory_entry(self):
        self.assertPasses()

    def test_fails_naming_an_extension_missing_from_the_inventory(self):
        self.repo.write(
            "dot_Brewfile", 'vscode "eamodio.gitlens"\nvscode "ms-python.python"\n'
        )
        self.assertFailsMentioning(
            "VS Code extension", "'ms-python.python'", "docs/inventory.md"
        )

    def test_fails_naming_an_inventory_entry_for_a_removed_extension(self):
        self.repo.write("dot_Brewfile", "")
        self.assertFailsMentioning("'eamodio.gitlens'", "docs/inventory.md")


class GlobalPythonPackagesTest(CheckTestCase):
    def setUp(self):
        super().setUp()
        self.repo.write("dot_Brewfile", 'uv "ruff"\n')
        self.repo.write(
            "docs/inventory.md",
            INVENTORY_HEADER
            + BREWFILE_ENTRY
            + "## Global Python packages (uv)\n\n"
            + "- **[ruff](https://docs.astral.sh/ruff/)**: Linter.\n",
        )

    def test_passes_when_every_package_has_an_inventory_entry(self):
        self.assertPasses()

    def test_fails_naming_a_package_missing_from_the_inventory(self):
        self.repo.write("dot_Brewfile", 'uv "ruff"\nuv "pre-commit"\n')
        self.assertFailsMentioning(
            "Global Python package", "'pre-commit'", "docs/inventory.md"
        )

    def test_fails_naming_an_inventory_entry_for_a_removed_package(self):
        self.repo.write("dot_Brewfile", "")
        self.assertFailsMentioning("'ruff'", "docs/inventory.md")


class GlobalNodePackagesTest(CheckTestCase):
    def setUp(self):
        super().setUp()
        self.repo.write(
            ".chezmoidata/packages.toml", '[packages]\nnode = ["skills@latest"]\n'
        )
        self.repo.write(
            "docs/inventory.md",
            INVENTORY_HEADER
            + "## Global Node packages (ni)\n\n"
            + "- **[skills](https://github.com/vercel-labs/skills)**: Agent skills.\n",
        )

    def test_passes_when_every_package_has_an_inventory_entry(self):
        self.assertPasses()

    def test_fails_naming_a_package_missing_from_the_inventory(self):
        self.repo.write(
            ".chezmoidata/packages.toml",
            '[packages]\nnode = ["skills@latest", "@antfu/ni@^24"]\n',
        )
        self.assertFailsMentioning(
            "Global Node package", "'@antfu/ni'", "docs/inventory.md"
        )

    def test_fails_naming_an_inventory_entry_for_a_removed_package(self):
        self.repo.write(".chezmoidata/packages.toml", "[packages]\nnode = []\n")
        self.assertFailsMentioning("'skills'", "docs/inventory.md")


class MiseToolsTest(CheckTestCase):
    MISE_CONFIG = "private_dot_config/mise/config.toml"
    MISE_CONFIG_ENTRY = (
        "- **[`~/.config/mise/config.toml`](https://mise.jdx.dev/configuration.html)**: Tools.\n"
    )

    def setUp(self):
        super().setUp()
        self.repo.write(self.MISE_CONFIG, '[tools]\nnode = "lts"\n')
        self.repo.write(
            "docs/inventory.md",
            INVENTORY_HEADER
            + self.MISE_CONFIG_ENTRY
            + "## JavaScript toolchain (mise)\n\n"
            + "- **[node](https://nodejs.org/docs)**: Runtime.\n",
        )

    def test_passes_when_every_tool_has_an_inventory_entry(self):
        self.assertPasses()

    def test_fails_naming_a_tool_missing_from_the_inventory(self):
        self.repo.write(self.MISE_CONFIG, '[tools]\nnode = "lts"\nbun = "latest"\n')
        self.assertFailsMentioning("mise tool", "'bun'", "docs/inventory.md")

    def test_fails_naming_an_inventory_entry_for_a_removed_tool(self):
        self.repo.write(self.MISE_CONFIG, "[settings]\n")
        self.assertFailsMentioning("'node'", "docs/inventory.md")


class ChezmoiRunFilesTest(CheckTestCase):
    def setUp(self):
        super().setUp()
        self.repo.write("run_once_install-fonts.sh", "#!/bin/sh\n")
        self.repo.write(
            "docs/inventory.md",
            INVENTORY_HEADER
            + "## Chezmoi run files\n\n"
            + "- **[run_once_install-fonts.sh](https://www.chezmoi.io/user-guide/use-scripts-to-perform-actions/)**: Fonts.\n",
        )

    def test_passes_when_every_run_file_has_an_inventory_entry(self):
        self.assertPasses()

    def test_fails_naming_a_run_file_missing_from_the_inventory(self):
        self.repo.write(".chezmoiscripts/run_onchange_after_50-dock.sh.tmpl", "")
        self.assertFailsMentioning(
            "Chezmoi run file",
            "'run_onchange_after_50-dock.sh.tmpl'",
            "docs/inventory.md",
        )

    def test_fails_naming_an_inventory_entry_for_a_removed_run_file(self):
        self.repo.remove("run_once_install-fonts.sh")
        self.assertFailsMentioning("'run_once_install-fonts.sh'", "docs/inventory.md")


class ConfigFilesTest(CheckTestCase):
    def setUp(self):
        super().setUp()
        self.repo.write("dot_zshrc", "export EDITOR=nvim\n")
        self.repo.write(KARABINER_PATH, "{}\n")
        self.repo.write(
            "docs/inventory.md",
            INVENTORY_HEADER + "## Config files\n\n" + KARABINER_ENTRY + ZSHRC_ENTRY,
        )

    def test_passes_when_every_config_file_has_an_inventory_entry(self):
        self.assertPasses()

    def test_fails_naming_a_config_file_missing_from_the_inventory(self):
        self.repo.write("dot_gitconfig", "[pull]\n\trebase = true\n")
        self.assertFailsMentioning("Config file", "'~/.gitconfig'", "docs/inventory.md")

    def test_fails_naming_an_inventory_entry_for_a_removed_config_file(self):
        self.repo.remove("dot_zshrc")
        self.assertFailsMentioning("'~/.zshrc'", "docs/inventory.md")

    def test_names_a_template_by_the_file_it_renders(self):
        self.repo.write("dot_config/starship.toml.tmpl", "add_newline = false\n")
        self.assertFailsMentioning("Config file", "'~/.config/starship.toml'")

    def test_names_the_chezmoi_config_template_by_the_config_it_renders(self):
        self.repo.write(".chezmoi.toml.tmpl", "[data]\n")
        self.assertFailsMentioning("Config file", "'~/.config/chezmoi/chezmoi.toml'")


class TrackedFilesTest(CheckTestCase):
    def setUp(self):
        super().setUp()
        self.repo.write("dot_Brewfile", "")
        self.repo.write("docs/inventory.md", INVENTORY_HEADER + BREWFILE_ENTRY)
        self.repo.write("README.md", "# Dotfiles\n")

    def test_passes_when_every_tracked_file_is_accounted_for(self):
        self.assertPasses()

    def test_fails_naming_an_unrecognized_tracked_file(self):
        self.repo.write("bin/executable_backup.sh", "#!/bin/sh\n")
        self.assertFailsMentioning(
            "bin/executable_backup.sh", "not accounted for", "scripts/check-docs.py"
        )

    def test_ignores_untracked_files(self):
        (self.repo.root / "notes.txt").write_text("scratch\n")
        self.assertPasses()

    def test_forgets_a_file_once_it_is_deleted(self):
        self.repo.write("bin/executable_backup.sh", "#!/bin/sh\n")
        self.repo.remove("bin/executable_backup.sh")
        self.assertPasses()


USAGE_HEADER = "# Usage\n\n"


def usage_table(*rows: tuple[str, str]) -> str:
    """A usage guide with one `Alias | Runs` table."""
    lines = ["## Git", "", "| Alias | Runs |", "| --- | --- |"]
    lines += [f"| {alias} | {runs} |" for alias, runs in rows]
    return USAGE_HEADER + "\n".join(lines) + "\n"


# dot_zshrc is also a config file, so fixtures that write it need this entry.
ZSHRC_ENTRY = "- **[`~/.zshrc`](https://zsh.sourceforge.io/Doc/)**: Shell.\n"
ZPROFILE_ENTRY = "- **[`~/.zprofile`](https://zsh.sourceforge.io/Doc/)**: Login.\n"
ZSHENV_ENTRY = "- **[`~/.zshenv`](https://zsh.sourceforge.io/Doc/)**: Every shell.\n"


class ShellAliasesTest(CheckTestCase):
    def setUp(self):
        super().setUp()
        self.repo.write("dot_zshrc", "alias gs='git status'\nalias gc='git commit'\n")
        self.repo.write("docs/inventory.md", INVENTORY_HEADER + ZSHRC_ENTRY)
        self.repo.write(
            "docs/usage.md",
            usage_table(("`gs`", "`git status`"), ("`gc`", "`git commit`")),
        )

    def test_passes_when_every_shell_alias_is_in_a_usage_table(self):
        self.assertPasses()

    def test_fails_naming_a_shell_alias_missing_from_the_usage_guide(self):
        self.repo.write(
            "dot_zshrc",
            "alias gs='git status'\nalias gc='git commit'\nalias gp='git push'\n",
        )
        self.assertFailsMentioning("Shell alias", "'gp'", "docs/usage.md")

    def test_fails_naming_a_usage_entry_for_a_removed_shell_alias(self):
        self.repo.write("dot_zshrc", "alias gs='git status'\n")
        self.assertFailsMentioning("'gc'", "docs/usage.md")

    def test_excuses_no_shell_alias(self):
        self.repo.write(
            "dot_zshrc",
            "alias gs='git status'\nalias gc='git commit'\nalias ll='eza -lah'\n",
        )
        self.assertFailsMentioning("Shell alias", "'ll'", "docs/usage.md")

    def test_counts_several_aliases_in_one_cell(self):
        self.repo.write("dot_zshrc", "alias gs='git status'\nalias gst='git status'\n")
        self.repo.write("docs/usage.md", usage_table(("`gs`, `gst`", "`git status`")))
        self.assertPasses()

    def test_counts_only_code_spans_in_the_first_cell_of_a_table_row(self):
        self.repo.write(
            "docs/usage.md",
            usage_table(("`gs`", "`git status`"), ("Commit", "`gc`"))
            + "\nCommit with `gc`.\n",
        )
        self.assertFailsMentioning("Shell alias", "'gc'")

    def test_fails_naming_an_alias_from_zprofile_missing_from_the_usage_guide(self):
        self.repo.write("dot_zprofile", "alias up='cd ..'\n")
        self.repo.write("docs/inventory.md", INVENTORY_HEADER + ZSHRC_ENTRY + ZPROFILE_ENTRY)
        self.assertFailsMentioning("Shell alias", "'up'", "docs/usage.md")

    def test_ignores_aliases_in_code_blocks(self):
        self.repo.write(
            "docs/usage.md",
            usage_table(("`gs`", "`git status`"), ("`gc`", "`git commit`"))
            + "\n```md\n| `gx` | `git x` |\n```\n",
        )
        self.assertPasses()


ZSHRC_WITH_FUNCTIONS = """\
vz() {
  chezmoi edit --apply ~/.zshrc
}
function mkcd {
  mkdir -p "$1" && cd "$1"
}
"""


class ShellFunctionsTest(CheckTestCase):
    def setUp(self):
        super().setUp()
        self.repo.write("dot_zshrc", ZSHRC_WITH_FUNCTIONS)
        self.repo.write("docs/inventory.md", INVENTORY_HEADER + ZSHRC_ENTRY)
        self.repo.write(
            "docs/usage.md",
            usage_table(("`vz`", "`chezmoi edit --apply`"), ("`mkcd`", "`mkdir -p`")),
        )

    def test_passes_when_every_shell_function_is_in_a_usage_table(self):
        self.assertPasses()

    def test_fails_naming_a_shell_function_missing_from_the_usage_guide(self):
        self.repo.write(
            "dot_zshrc", ZSHRC_WITH_FUNCTIONS + "function up() {\n  cd ..\n}\n"
        )
        self.assertFailsMentioning("Shell function", "'up'", "docs/usage.md")

    def test_fails_naming_a_usage_entry_for_a_removed_shell_function(self):
        self.repo.write("dot_zshrc", ZSHRC_WITH_FUNCTIONS.split("function mkcd")[0])
        self.assertFailsMentioning("'mkcd'", "docs/usage.md")

    def test_fails_naming_a_shell_function_from_zshenv_missing_from_the_usage_guide(self):
        self.repo.write("dot_zshenv", "up() {\n  cd ..\n}\n")
        self.repo.write("docs/inventory.md", INVENTORY_HEADER + ZSHRC_ENTRY + ZSHENV_ENTRY)
        self.assertFailsMentioning("Shell function", "'up'", "docs/usage.md")

    def test_passes_when_functions_from_every_zsh_config_file_are_documented(self):
        self.repo.write("dot_zshenv", "up() {\n  cd ..\n}\n")
        self.repo.write("dot_zprofile", "alias home='cd ~'\n")
        self.repo.write(
            "docs/inventory.md",
            INVENTORY_HEADER + ZSHRC_ENTRY + ZPROFILE_ENTRY + ZSHENV_ENTRY,
        )
        self.repo.write(
            "docs/usage.md",
            usage_table(
                ("`vz`", "`chezmoi edit --apply`"),
                ("`mkcd`", "`mkdir -p`"),
                ("`up`", "`cd ..`"),
                ("`home`", "`cd ~`"),
            ),
        )
        self.assertPasses()

    def test_ignores_functions_registered_as_line_editor_widgets(self):
        self.repo.write(
            "dot_zshrc",
            ZSHRC_WITH_FUNCTIONS
            + "function zle-keymap-select() {\n  :\n}\nzle -N zle-keymap-select\n"
            + "_expand() {\n  :\n}\nzle -N expand-alias _expand\n",
        )
        self.assertPasses()


GITCONFIG = """\
[pull]
\trebase = true
[alias]
    lg = log --graph --all
\tst = status
[core]
\tpager = delta
"""

# dot_gitconfig is also a config file, so fixtures that write it need this entry.
GITCONFIG_ENTRY = "- **[`~/.gitconfig`](https://git-scm.com/docs/git-config)**: Git.\n"


class GitAliasesTest(CheckTestCase):
    def setUp(self):
        super().setUp()
        self.repo.write("dot_gitconfig", GITCONFIG)
        self.repo.write("docs/inventory.md", INVENTORY_HEADER + GITCONFIG_ENTRY)
        self.repo.write(
            "docs/usage.md",
            usage_table(("`git lg`", "`git log --graph`"), ("`git st`", "`git status`")),
        )

    def test_passes_when_every_git_alias_is_in_a_usage_table(self):
        self.assertPasses()

    def test_fails_naming_a_git_alias_missing_from_the_usage_guide(self):
        self.repo.write("dot_gitconfig", GITCONFIG + "[alias]\n\tco = checkout\n")
        self.assertFailsMentioning("Git alias", "'git co'", "docs/usage.md")

    def test_fails_naming_a_usage_entry_for_a_removed_git_alias(self):
        self.repo.write("dot_gitconfig", GITCONFIG.replace("\tst = status\n", ""))
        self.assertFailsMentioning("'git st'", "docs/usage.md")

    def test_ignores_settings_outside_the_alias_section(self):
        self.repo.write("dot_gitconfig", "[pull]\n\trebase = true\n")
        self.repo.write("docs/usage.md", USAGE_HEADER)
        self.assertPasses()


GH_CONFIG_PATH = "private_dot_config/gh/private_config.yml"
GH_CONFIG = """\
version: 1
git_protocol: https
# Aliases allow you to create nicknames for gh commands
aliases:
    co: pr checkout
    # A comment inside the block
    pv: pr view --web
http_unix_socket:
"""

# The gh config is also a config file, so fixtures that write it need this entry.
GH_CONFIG_ENTRY = (
    "- **[`~/.config/gh/config.yml`](https://cli.github.com/manual/gh_config)**: gh.\n"
)


class GhAliasesTest(CheckTestCase):
    def setUp(self):
        super().setUp()
        self.repo.write(GH_CONFIG_PATH, GH_CONFIG)
        self.repo.write("docs/inventory.md", INVENTORY_HEADER + GH_CONFIG_ENTRY)
        self.repo.write(
            "docs/usage.md",
            usage_table(("`gh co`", "`gh pr checkout`"), ("`gh pv`", "`gh pr view --web`")),
        )

    def test_passes_when_every_gh_alias_is_in_a_usage_table(self):
        self.assertPasses()

    def test_fails_naming_a_gh_alias_missing_from_the_usage_guide(self):
        self.repo.write(
            GH_CONFIG_PATH, GH_CONFIG.replace("aliases:\n", "aliases:\n    il: issue list\n")
        )
        self.assertFailsMentioning("gh alias", "'gh il'", "docs/usage.md")

    def test_fails_naming_a_usage_entry_for_a_removed_gh_alias(self):
        self.repo.write(GH_CONFIG_PATH, GH_CONFIG.replace("    pv: pr view --web\n", ""))
        self.assertFailsMentioning("'gh pv'", "docs/usage.md")

    def test_passes_with_no_aliases(self):
        self.repo.write(GH_CONFIG_PATH, "version: 1\naliases: {}\n")
        self.repo.write("docs/usage.md", USAGE_HEADER)
        self.assertPasses()


def key_remap_table(*rows: tuple[str, str]) -> str:
    """A usage guide with one `Key | Does` table."""
    lines = ["## Keyboard & mouse", "", "| Key | Does |", "| --- | --- |"]
    lines += [f"| {key} | {does} |" for key, does in rows]
    return USAGE_HEADER + "\n".join(lines) + "\n"


KARABINER_PATH = "private_dot_config/private_karabiner/private_karabiner.json"
CAPS_LOCK_RULE = "Caps Lock to Escape on single press, Caps Lock on press and hold."
HYPER_RULE = "Fn + Letter -> Hyper + Letter"


def karabiner_config(*descriptions: str) -> str:
    rules = [{"description": d, "manipulators": []} for d in descriptions]
    return json.dumps(
        {
            "profiles": [
                {
                    "name": "Default profile",
                    "complex_modifications": {"rules": rules},
                    "simple_modifications": [
                        {
                            "from": {"key_code": "right_option"},
                            "to": [{"key_code": "delete_forward"}],
                        }
                    ],
                }
            ]
        }
    )


# The Karabiner JSON is also a config file, so fixtures that write it need this entry.
KARABINER_ENTRY = (
    "- **[`~/.config/karabiner/karabiner.json`](https://karabiner-elements.pqrs.org/docs/)**: Remaps.\n"
)


class KarabinerRulesTest(CheckTestCase):
    def setUp(self):
        super().setUp()
        self.repo.write(KARABINER_PATH, karabiner_config(CAPS_LOCK_RULE, HYPER_RULE))
        self.repo.write("docs/inventory.md", INVENTORY_HEADER + KARABINER_ENTRY)
        self.repo.write(
            "docs/usage.md",
            key_remap_table(
                (f"Caps Lock: `{CAPS_LOCK_RULE}`", "Escape when tapped"),
                (f"`{HYPER_RULE}`", "Hyper combinations"),
                ("Right Option", "Forward delete"),
            ),
        )

    def test_passes_when_every_rule_is_in_a_key_remap_table(self):
        self.assertPasses()

    def test_fails_naming_a_rule_missing_from_the_usage_guide(self):
        self.repo.write(
            KARABINER_PATH,
            karabiner_config(CAPS_LOCK_RULE, HYPER_RULE, "Right Command to Hyper"),
        )
        self.assertFailsMentioning("Key remap", "'Right Command to Hyper'", "docs/usage.md")

    def test_fails_naming_a_usage_entry_for_a_removed_rule(self):
        self.repo.write(KARABINER_PATH, karabiner_config(CAPS_LOCK_RULE))
        self.assertFailsMentioning(f"'{HYPER_RULE}'", "docs/usage.md")

    def test_fails_naming_a_rule_that_is_only_in_an_alias_table(self):
        self.repo.write(
            "docs/usage.md",
            key_remap_table((f"Caps Lock: `{CAPS_LOCK_RULE}`", "Escape when tapped"))
            + "\n"
            + usage_table((f"`{HYPER_RULE}`", "Hyper combinations")),
        )
        self.assertFailsMentioning(
            "missing an entry for Key remap", f"'{HYPER_RULE}'", "docs/usage.md"
        )


class RepositoryTest(unittest.TestCase):
    def test_passes_on_this_repository(self):
        result = subprocess.run(
            [sys.executable, str(SCRIPT)], capture_output=True, text=True
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
