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
            + "- **[bat](https://github.com/sharkdp/bat)**: Pager.\n",
        )
        self.assertPasses()

    def test_documents_a_tapped_formula_by_its_short_name(self):
        self.repo.write("dot_Brewfile", 'brew "bat"\nbrew "acme/tap/gizmo"\n')
        self.assertFailsMentioning("'gizmo'")
        self.repo.write(
            "docs/inventory.md",
            INVENTORY_HEADER
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


class TrackedFilesTest(CheckTestCase):
    def setUp(self):
        super().setUp()
        self.repo.write("dot_Brewfile", "")
        self.repo.write("docs/inventory.md", INVENTORY_HEADER)
        self.repo.write("README.md", "# Dotfiles\n")

    def test_passes_when_every_tracked_file_is_accounted_for(self):
        self.assertPasses()

    def test_fails_naming_an_unrecognized_tracked_file(self):
        self.repo.write("dot_wgetrc", "quiet = on\n")
        self.assertFailsMentioning("dot_wgetrc", "scripts/check-docs.py")

    def test_ignores_untracked_files(self):
        (self.repo.root / "notes.txt").write_text("scratch\n")
        self.assertPasses()

    def test_forgets_a_file_once_it_is_deleted(self):
        self.repo.write("dot_wgetrc", "quiet = on\n")
        self.repo.remove("dot_wgetrc")
        self.assertPasses()


class RepositoryTest(unittest.TestCase):
    def test_passes_on_this_repository(self):
        result = subprocess.run(
            [sys.executable, str(SCRIPT)], capture_output=True, text=True
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
