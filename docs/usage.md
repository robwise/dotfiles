# Usage

How to use this setup day to day, by activity.

<!--
Template for this document. `scripts/check-docs.py` enforces the alias tables.

Sections, in this order:

1. Terminal: Ghostty, MonoLisa, Catppuccin, starship, zsh vi mode and `jj`,
   fzf, zoxide, eza aliases, a pointer to `vz`
2. Git: aliases, pull/rebase/rerere/fetch defaults, delta, gh, scmpuff
   numbered files
3. Node: mise, ni, pnpm global installs, Corepack/Yarn handling
4. Python: uv, ruff, pre-commit
5. Editing: nvim as `$EDITOR`, VS Code/Cursor with the neovim extension
6. Keyboard & mouse: Karabiner remaps, press-and-hold off, LinearMouse
7. Finder
8. Documents: pandoc, Eisvogel, TinyTeX, typst
9. Dotfiles: chezmoi apply/diff/edit, `vz`, `dotsync`, adding a package

Each section has the following, leaving out what it doesn't need:

- An intro of one to three sentences on what's configured and why. Keep it
  very concise, but write for a reader who has forgotten what each setting
  means.
- An `Aliases` table (`Alias | Runs`) or a `Key remaps` table (`Key | Does`).
  Put each alias in the first cell as a code span; aliases for the same
  command can share a row. Write git and gh aliases as you type them
  (`git lg`, `gh co`). Describe what actually runs when you type the alias.
- A `How to` list of task → command.
- A closing line linking the section's tools to their inventory entries.
  Inventory entries are bullets without anchors, so link the heading they sit
  under, such as `inventory.md#homebrew-formulae`.

```md
## Git

`git pull` rebases instead of merging. ...

### Aliases

| Alias | Runs |
| --- | --- |
| `gs` | `git status` with numbered files |

### How to

- Stage files by number: `ga 1 3`

Inventory: [git](inventory.md#homebrew-formulae).
```
-->

## Git

`git pull` replays your local commits on top of the remote's instead of
making a merge commit (rebase), stashing uncommitted changes first and
restoring them afterward (autostash). Git remembers how you resolved each
conflict and reapplies that resolution if the same conflict comes back
(rerere), `git fetch` deletes your copies of branches that were deleted on the
remote (prune), and conflict markers also show the text both sides started
from (zdiff3). Diffs, logs, and `git add -p` go through delta, which shows
changes side by side with line numbers and highlights moved lines.

### Aliases

| Alias | Runs |
| --- | --- |
| `gs` | `git status` with numbered files (scmpuff) |
| `gst` | `git status` |
| `gaa` | `git add -A` |
| `gc` | `git commit` |
| `gcm` | `git commit -m` |
| `gcma` | `git commit --amend` |
| `gp`, `gps` | `git push` |
| `gpsf` | `git push --force-with-lease` |
| `gpl` | `git pull` |
| `gco` | `git checkout` |
| `gcb` | `git checkout -b` |
| `gd` | `git diff` |
| `gds` | `git diff --staged` |
| `gl` | `git log` |
| `grb` | `git rebase` |
| `grbi` | `git rebase -i` |
| `git lg` | `git log --graph --all`, one line per commit with branches, age, and author |
| `gh co` | `gh pr checkout` |

### How to

- See what changed, with each file numbered: `gs`
- Stage files by number: `ga 1 3` or `ga 2-4` (prints the numbered status
  again)
- Diff, check out, or unstage files by number: `gd 2`, `gco 2`, `grs 1`
- Use the numbers in other git commands, such as `git commit`, `git rm`, or
  `git restore`; in non-git commands, use `$e1`, `$e2`, and so on
- Stage everything and commit: `gaa`, then `gcm "message"`
- Add staged changes to the last commit: `gcma`
- Push after a rebase or amend: `gpsf` (refuses if the remote has commits you
  haven't fetched)
- Tidy up commits before pushing: `grbi main`
- See every branch as a graph: `git lg`
- Jump between files in a diff: `n` and `N`
- Check out a pull request: `gh co 123`

Inventory: [git](inventory.md#homebrew-formulae),
[gh](inventory.md#homebrew-formulae),
[scmpuff](inventory.md#homebrew-formulae).
