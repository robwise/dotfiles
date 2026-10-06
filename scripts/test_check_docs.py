"""Tests for scripts/check-docs.py.

Each test builds a fixture repository (a temporary git repository) and runs
the check against it through its command-line interface.

Run with: uv run python -m unittest discover -s scripts
"""

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
        self.repo.write("dot_zshrc", "alias ll='ls -l'\n")
        self.repo.write(
            "private_dot_config/private_karabiner/private_karabiner.json", "{}\n"
        )
        self.repo.write(
            "docs/inventory.md",
            INVENTORY_HEADER
            + "## Config files\n\n"
            + "- **[`~/.config/karabiner/karabiner.json`](https://karabiner-elements.pqrs.org/docs/)**: Remaps.\n"
            + "- **[`~/.zshrc`](https://zsh.sourceforge.io/Doc/)**: Shell.\n",
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


class RepositoryTest(unittest.TestCase):
    def test_passes_on_this_repository(self):
        result = subprocess.run(
            [sys.executable, str(SCRIPT)], capture_output=True, text=True
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
