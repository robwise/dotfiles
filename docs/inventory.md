# Inventory

Every package, font, config file, and chezmoi run file this repository sets up.

<!--
Template for this document. `scripts/check-docs.py` enforces the entries.

Headings, in this order:

1. Homebrew formulae
2. Homebrew casks (not fonts)
3. Fonts (the Nerd Font cask plus MonoLisa from `fonts/`)
4. VS Code extensions
5. Global Python packages (uv)
6. Global Node packages (ni)
7. JavaScript toolchain (mise): node, pnpm, bun, yarn
8. Config files
9. Chezmoi run files

Taps get no entries. One alphabetical bullet per entry: a bold name that
links to upstream docs, then the purpose, then our choices. Name the installer
only when the heading doesn't already say it (for example, under Fonts). Use
no other links. A tapped formula's name drops the tap (`owner/tap/name` is
`name`).

```md
## JavaScript toolchain (mise)

- **[node](https://nodejs.org/docs)**: JavaScript runtime. Follows LTS; projects can pin a version with `.nvmrc`/`.node-version`.
```
-->

## Homebrew formulae

- **[bat](https://github.com/sharkdp/bat)**: `cat` with syntax highlighting and Git integration.
- **[chezmoi](https://www.chezmoi.io/)**: Applies this repository to the home directory. The source checkout lives wherever it was cloned with `chezmoi init --source`, and the config template remembers that path.
- **[eza](https://eza.rocks)**: Modern `ls`. Shell aliases replace `ls` with eza and add long and tree listings with icons and Git status.
- **[fd](https://github.com/sharkdp/fd)**: Fast, user-friendly alternative to `find`.
- **[fzf](https://junegunn.github.io/fzf/)**: Command-line fuzzy finder. `.zshrc` loads its zsh key bindings and completion.
- **[gh](https://cli.github.com/manual/)**: GitHub CLI. Uses HTTPS for Git operations and defines a `co` alias for `gh pr checkout`.
- **[git](https://git-scm.com/doc)**: Version control. Pulls rebase with auto-stash, rerere is on, fetch prunes, conflicts use `zdiff3`, and delta pages diffs side by side.
- **[gogcli](https://gogcli.sh)**: Google Workspace CLI, run as `gog`.
- **[jq](https://jqlang.github.io/jq/manual/)**: Command-line JSON processor.
- **[librsvg](https://gitlab.gnome.org/GNOME/librsvg)**: SVG rendering library; provides `rsvg-convert` so pandoc can put SVG images in PDFs.
- **[mise](https://mise.jdx.dev/)**: Runtime manager for node, pnpm, bun, and yarn. `.zshrc` activates it, and node follows LTS unless a project has an `.nvmrc` or `.node-version`.
- **[neovim](https://neovim.io/doc/)**: Terminal editor, set as `$EDITOR` and `$VISUAL`.
- **[ni](https://github.com/antfu-collective/ni)**: Runs the right Node package manager for a project from its lockfile. `.nirc` falls back to pnpm and uses pnpm for global installs.
- **[pandoc](https://pandoc.org/MANUAL.html)**: Converts between markup formats. A chezmoi run file adds TinyTeX and the Eisvogel template for PDF output.
- **[ripgrep](https://github.com/BurntSushi/ripgrep)**: Fast recursive search, run as `rg`.
- **[scmpuff](https://github.com/mroth/scmpuff)**: Numbers the files in `git status` output so later commands can refer to them by number. `.zshrc` initializes it.
- **[spogo](https://github.com/openclaw/spogo)**: Spotify CLI.
- **[starship](https://starship.rs/)**: Shell prompt, initialized in `.zshrc` with default settings.
- **[summarize](https://summarize.sh)**: AI tool that summarizes web pages, files, and media.
- **[todoist-cli](https://github.com/LuoAndOrder/todoist-rs)**: Todoist CLI.
- **[tree-sitter-cli](https://tree-sitter.github.io/tree-sitter/)**: Tree-sitter parser generator, used to build Neovim syntax parsers.
- **[typst](https://typst.app/docs/)**: Markup-based typesetting system.
- **[uv](https://docs.astral.sh/uv/)**: Python package and project manager. Installs the Brewfile's global Python packages into `~/.local/bin`, which `.zprofile` puts on `PATH`.
- **[zoxide](https://github.com/ajeetdsouza/zoxide)**: `cd` that learns frequent directories, used as `z`. `.zshrc` initializes it.
