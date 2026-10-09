<!--
Template for this document.

Sections, in this order: Terminal, Git, Node, Python, Editing, Keyboard &
mouse, Finder, Documents, Dotfiles.

Each section has the following, leaving out what it doesn't need:

- An intro of one to three sentences on what's configured and why, for a
  reader who has forgotten what each setting means.
- `### Aliases`: an `Alias | Runs` table. Put each alias in the first cell as
  a code span (git and gh aliases as typed: `git lg`); aliases for the same
  command can share a row. Say what actually runs.
- `### Key remaps`: a `Key | Does` table. Name the key, then put the Karabiner
  rule's `description` verbatim in a code span: ``Caps Lock: `Caps Lock to
  Escape ...` ``. A remap without a description gets plain text only.
- `### How to`: a list of task → command.
- A closing line linking the section's packages and config files to the
  inventory heading they sit under: `inventory.md#homebrew-formulae`.

In a table's first cell, use code spans only for entries.
-->

# Usage

How to use this setup day to day, by activity.

## Terminal

Ghostty is the terminal: it uses the Catppuccin Mocha color theme and the
MonoLisa coding font, and falls back to the Nerd Font symbols for the icons
that eza and other commands print. zsh draws its prompt with starship and runs
in vi mode: you start in insert mode, Esc (or typing `jj` quickly) switches
to normal mode for Vim motions, and the cursor is a block in normal mode and a
beam in insert mode. fzf adds fuzzy search to history and file paths, zoxide
remembers the directories you visit, and eza replaces `ls`.

### Aliases

| Alias | Runs |
| --- | --- |
| `ls` | `eza` |
| `ll` | `eza -lah --icons --git`: every file, one per line, with sizes, icons, and Git status |
| `lt` | `eza --tree --level=2`: a tree two levels deep |
| `la` | `eza -la --tree --level=2 --git`: a two-level tree of every file, with details and Git status |
| `..` | `cd ..` |

### How to

- Leave insert mode to edit the command line with Vim motions: Esc or `jj`
- Search shell history: Ctrl-R, then type part of the command
- Insert a file path into the command: Ctrl-T
- Jump to a directory you've visited before: `z dotfiles` (`zi` to pick from a
  list)
- Edit `.zshrc` and apply it: `vz` (see [Dotfiles](#dotfiles))

Inventory: [ghostty](inventory.md#homebrew-casks),
[MonoLisa](inventory.md#fonts),
[font-symbols-only-nerd-font](inventory.md#fonts),
[starship](inventory.md#homebrew-formulae),
[fzf](inventory.md#homebrew-formulae),
[zoxide](inventory.md#homebrew-formulae),
[eza](inventory.md#homebrew-formulae),
[`~/.config/ghostty/config.ghostty`](inventory.md#config-files),
[`~/.zshrc`](inventory.md#config-files).

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
- Diff a file by number: `gd 2`
- Throw away your changes to a file: `gco 2`
- Unstage a file: `grs 1`
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

## Node

mise installs and switches the JavaScript toolchain: node follows the current
LTS release unless a project pins a version in `.nvmrc` or `.node-version`,
and pnpm, bun, and yarn track their latest releases. ni works out which
package manager a project uses from its lockfile and runs the matching
command, so you type the same commands everywhere; with no lockfile it uses
pnpm. Global Node packages go through `ni -g`, which also uses pnpm, so they
land in `~/Library/pnpm` and are on `PATH` in every project, and setup turns
off Corepack's Yarn launcher so that `yarn` runs mise's Yarn.

### How to

- Install a project's dependencies: `ni`
- Add a dependency: `ni vite` (`ni @types/node -D` for a dev dependency)
- Remove a dependency: `nun webpack`
- Install exactly what the lockfile says, as CI does: `nci`
- Upgrade dependencies: `nup` (`nup -i` to choose)
- Run a `package.json` script: `nr dev` (`nr` alone to pick one, `nr -` to
  rerun the last)
- Run a package's command without installing it: `nlx vitest`
- See which package manager ni picked: `na`
- Use a different Node version in a project: put the version in `.nvmrc` or
  `.node-version`
- See which node, pnpm, bun, and yarn versions are active: `mise ls`
- Install a global Node package on every machine: add it to `packages.node`
  in `.chezmoidata/packages.toml`, then `chezmoi apply`
- Find agent skills: `skills find`
- Install an agent skill for every project: `skills add <source> -g`
  (without `-g`, it installs into the current project)
- List or update installed skills: `skills list`, `skills update`

Inventory: [mise](inventory.md#homebrew-formulae),
[ni](inventory.md#homebrew-formulae),
[node, pnpm, bun, yarn](inventory.md#javascript-toolchain-mise),
[skills](inventory.md#global-node-packages-ni),
[`~/.nirc`](inventory.md#config-files),
[`~/.config/mise/config.toml`](inventory.md#config-files).

## Python

uv installs the Brewfile's global Python packages, each in its own
environment, and puts their commands in `~/.local/bin`. ruff lints and formats
Python. pre-commit runs a repository's checks before each commit.

### How to

- Lint and format Python: `ruff check .`, `ruff format .`
- Run a Python package's command once without installing it:
  `uvx <package>`
- Run a script, including one that lists its own dependencies: `uv run
  script.py`
- Turn on the hooks in a repository that has a `.pre-commit-config.yaml`:
  `pre-commit install`
- Run a repository's hooks without committing: `pre-commit run --all-files`

Inventory: [uv](inventory.md#homebrew-formulae),
[pre-commit, ruff](inventory.md#global-python-packages-uv).

## Editing

nvim (Neovim) is `$EDITOR` and `$VISUAL`, so it opens whenever a command asks
for an editor, such as `git commit` or `chezmoi edit`. VS Code gets its
extensions from the Brewfile, including vscode-neovim, which runs a real
Neovim inside the editor so the same Vim motions work there; Cursor is
installed alongside it.

### How to

- Edit a file in the terminal: `nvim <file>`
- Open the current folder in VS Code: `code .`
- Open the current folder in Cursor: `cursor .`

Inventory: [neovim](inventory.md#homebrew-formulae),
[tree-sitter-cli](inventory.md#homebrew-formulae),
[visual-studio-code, cursor](inventory.md#homebrew-casks),
[asvetliakov.vscode-neovim](inventory.md#vs-code-extensions).

## Keyboard & mouse

Karabiner-Elements remaps keys system-wide: Caps Lock becomes Escape when
tapped, Fn plus any letter, number, or punctuation key sends a Hyper
combination (Shift+Option+Control+Command plus that key, which apps rarely
use on their own, so it is free for your global shortcuts), and Right Option
deletes forward. Press-and-hold is off everywhere, including VS Code and
Ghostty, so holding a key, such as a Vim motion, repeats it instead of
opening the accented-character menu. LinearMouse sets each mouse separately:
the BenQ ZOWIE mice have fixed pointer speeds without acceleration and
reversed scrolling, while the built-in trackpad keeps its usual scroll
direction.

### Key remaps

| Key | Does |
| --- | --- |
| Caps Lock: `Caps Lock to Escape on single press, Caps Lock on press and hold.` | Escape when tapped; Caps Lock when held |
| Fn + key: `Fn + Letter -> Left_Shift + Left_Option + Left_Control + Left_Command + Letter` | Shift+Option+Control+Command plus that key, for letters, numbers, and punctuation |
| Right Option | Forward delete |

### How to

- Type an accented character: Option plus the accent key, then the letter,
  such as Option-E then E for é
- Bind a global shortcut that won't clash: assign Fn plus a key in the app's
  shortcut settings (it records the Hyper combination)
- Turn a remap off for a while: Karabiner-Elements Settings → Complex
  Modifications (the rules carry the names in the table) or Simple
  Modifications
- Keep a change made in LinearMouse's settings: `chezmoi re-add`

Inventory: [linearmouse](inventory.md#homebrew-casks),
[`~/.config/karabiner/karabiner.json`](inventory.md#config-files),
[`~/.config/linearmouse/linearmouse.json`](inventory.md#config-files),
[run_onchange_after_10-macos-keyboard.sh.tmpl, run_once_macos-defaults.sh](inventory.md#chezmoi-run-files).

## Finder

Finder shows hidden files, opens new windows in column view, and searches the
current folder by default instead of the whole Mac. The title bar shows the
folder's full path, the path bar starts at your home folder, and Finder
doesn't leave `.DS_Store` files on network shares.

### How to

- Show or hide hidden files: ⌘⇧.
- Show the path bar: ⌥⌘P
- Copy the selected item's full path: ⌥⌘C
- Search the whole Mac instead of the current folder: choose This Mac under
  the search field

Inventory: [run_onchange_after_20-macos-finder.sh.tmpl](inventory.md#chezmoi-run-files).

## Documents

pandoc converts between document formats, such as Markdown to PDF or Word.
PDFs go through LaTeX from TinyTeX, the only TeX distribution on the Mac. It
lives in `~/Library/TinyTeX`, so installing it and its packages never asks for
a password, and `tlmgr` is its package manager. The Eisvogel template gives
PDFs a clean, styled layout, and librsvg lets them include SVG images. typst is
a faster, simpler typesetting system with its own markup.

Two settings in `.chezmoidata/packages.toml` in the source checkout decide what
every Mac gets. `packages.latex` lists the LaTeX packages that `chezmoi apply`
installs with `tlmgr`; changing the list makes the next apply install whatever
is missing. `eisvogel.version` pins the Eisvogel release that `chezmoi apply`
downloads into `~/.local/share/pandoc/templates`; changing it makes the next
apply download that release.

### How to

- Convert Markdown to a PDF: `pandoc notes.md -o notes.pdf --pdf-engine=xelatex`
- Use the Eisvogel layout: add `--template eisvogel`
- Convert Markdown to Word: `pandoc notes.md -o notes.docx`
- Install a LaTeX package that a PDF asks for, on every Mac: check its name
  with `tlmgr info <package>`, add it to `packages.latex`, then `chezmoi apply`
  (`tlmgr install <package>` alone installs it on this Mac only)
- Update the Eisvogel template: set `eisvogel.version` to a release number from
  the [Eisvogel releases](https://github.com/Wandmalfarbe/pandoc-latex-template/releases),
  without the leading `v`, then `chezmoi apply`
- Build a typst document: `typst compile doc.typ` (`typst watch doc.typ`
  rebuilds on save)

Inventory: [pandoc, librsvg, typst](inventory.md#homebrew-formulae),
[run_onchange_after_40-install-latex.sh.tmpl](inventory.md#chezmoi-run-files).

## Dotfiles

chezmoi copies this repository's files into your home directory. You edit the
source checkout (wherever `chezmoi init --source` cloned it), not the copies,
and `chezmoi apply` writes the copies and runs the chezmoi run files: `run_once`
files once per machine, `run_onchange` files whenever their contents, or the
files they track, change.

### Aliases

| Alias | Runs |
| --- | --- |
| `vz` | `chezmoi edit --apply ~/.zshrc`: opens the source `.zshrc` in nvim and applies it when you quit |
| `dotsync` | `brew bundle dump --global --force` (rewrites `~/.Brewfile` from what's installed), `chezmoi re-add` (copies changed config files back to the source), then commits everything in the source checkout as `sync dotfiles YYYY-MM-DD` and pushes |

### How to

- See what `chezmoi apply` would change: `chezmoi diff`
- Apply the source to your home directory: `chezmoi apply`
- Edit a config file: `chezmoi edit ~/.gitconfig` (add `--apply` to apply on
  quit)
- Pick up a `.zshrc` change in the current shell: `exec zsh`
- Keep a change you made directly in the home directory: `chezmoi re-add`
- Start managing a new config file: `chezmoi add ~/.config/<name>/<file>`
- Open a shell in the source checkout: `chezmoi cd`
- Pull the latest from GitHub and apply it: `chezmoi update`
- Add a Homebrew formula, cask, VS Code extension, or global Python package:
  add its line to `dot_Brewfile`, then `chezmoi apply` (or install it by hand
  and run `dotsync`)
- Add a global Node package: add it to `packages.node` in
  `.chezmoidata/packages.toml`, then `chezmoi apply`
- Document an addition: add an entry to [inventory.md](inventory.md), and an
  alias or key remap to this guide

Inventory: [chezmoi](inventory.md#homebrew-formulae),
[`~/.Brewfile`, `~/.config/chezmoi/chezmoi.toml`](inventory.md#config-files),
[chezmoi run files](inventory.md#chezmoi-run-files).
