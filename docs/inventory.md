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
links to upstream docs, then the purpose, then our choices. State each
setting once, on the config file or chezmoi run file entry that sets it. Name
the installer only when the heading doesn't already say it (for example,
under Fonts). Use no other links. A tapped formula's name drops the tap
(`owner/tap/name` is `name`).

```md
## JavaScript toolchain (mise)

- **[bun](https://bun.sh/docs)**: JavaScript runtime, bundler, and package manager.
```
-->

# Inventory

Every package, font, config file, and chezmoi run file this repository sets up.

## Homebrew formulae

- **[bat](https://github.com/sharkdp/bat)**: `cat` with syntax highlighting and Git integration.
- **[chezmoi](https://www.chezmoi.io/)**: Applies this repository to the home directory.
- **[eza](https://eza.rocks)**: Modern `ls`, with icons and Git status.
- **[fd](https://github.com/sharkdp/fd)**: Fast, user-friendly alternative to `find`.
- **[fzf](https://junegunn.github.io/fzf/)**: Command-line fuzzy finder.
- **[gh](https://cli.github.com/manual/)**: GitHub CLI.
- **[git](https://git-scm.com/doc)**: Version control.
- **[gogcli](https://gogcli.sh)**: Google Workspace CLI, run as `gog`.
- **[jq](https://jqlang.github.io/jq/manual/)**: Command-line JSON processor.
- **[librsvg](https://gitlab.gnome.org/GNOME/librsvg)**: SVG rendering library; provides `rsvg-convert` so pandoc can put SVG images in PDFs.
- **[mise](https://mise.jdx.dev/)**: Installs and switches the JavaScript toolchain: node, pnpm, bun, and yarn.
- **[neovim](https://neovim.io/doc/)**: Terminal editor.
- **[ni](https://github.com/antfu-collective/ni)**: Runs the right Node package manager for a project, detected from its `package.json` and lockfile.
- **[pandoc](https://pandoc.org/MANUAL.html)**: Converts between markup formats. A chezmoi run file adds TinyTeX and the Eisvogel template for PDF output.
- **[ripgrep](https://github.com/BurntSushi/ripgrep)**: Fast recursive search, run as `rg`.
- **[scmpuff](https://github.com/mroth/scmpuff)**: Numbers the files in `git status` output so later commands can refer to them by number.
- **[spogo](https://github.com/openclaw/spogo)**: Spotify CLI.
- **[starship](https://starship.rs/)**: Shell prompt, with default settings.
- **[summarize](https://summarize.sh)**: Summarizes web pages, files, and media with AI.
- **[todoist-cli](https://github.com/LuoAndOrder/todoist-rs)**: Todoist CLI.
- **[tree-sitter-cli](https://tree-sitter.github.io/tree-sitter/)**: Tree-sitter parser generator, used to build Neovim syntax parsers.
- **[typst](https://typst.app/docs/)**: Markup-based typesetting system.
- **[uv](https://docs.astral.sh/uv/)**: Python package and project manager. Installs the Brewfile's global Python packages.
- **[zoxide](https://github.com/ajeetdsouza/zoxide)**: `cd` that learns frequent directories, used as `z`.

## Homebrew casks

- **[basictex](https://www.tug.org/mactex/morepackages.html)**: Compact TeX Live distribution for macOS, with LaTeX engines and `tlmgr`.
- **[cursor](https://www.cursor.com/)**: AI code editor built on VS Code.
- **[ghostty](https://ghostty.org/)**: GPU-accelerated terminal emulator.
- **[linearmouse](https://linearmouse.org/)**: Per-device mouse and trackpad settings, configured in `~/.config/linearmouse/linearmouse.json`.
- **[visual-studio-code](https://code.visualstudio.com/)**: Code editor.

## Fonts

- **[font-symbols-only-nerd-font](https://github.com/ryanoasis/nerd-fonts)**: Nerd Font icon glyphs with no letters, installed as a Homebrew cask. Provides the icons that eza and other commands print.
- **[MonoLisaVariableItalic.ttf](https://www.monolisa.dev/)**: Italic styles of MonoLisa, a commercial monospaced coding font and Ghostty's font. Kept in `fonts/` and copied to `~/Library/Fonts` by `run_once_install-fonts.sh`.
- **[MonoLisaVariableNormal.ttf](https://www.monolisa.dev/)**: Upright styles of MonoLisa, Ghostty's font. Kept in `fonts/` and copied to `~/Library/Fonts` by `run_once_install-fonts.sh`.

## VS Code extensions

- **[aaron-bond.better-comments](https://marketplace.visualstudio.com/items?itemName=aaron-bond.better-comments)**: Highlights comments by type: alerts, questions, TODOs, and more.
- **[anthropic.claude-code](https://marketplace.visualstudio.com/items?itemName=anthropic.claude-code)**: Claude Code inside the editor.
- **[asvetliakov.vscode-neovim](https://marketplace.visualstudio.com/items?itemName=asvetliakov.vscode-neovim)**: Runs a real Neovim instance as the editor's Vim mode.
- **[christian-kohler.path-intellisense](https://marketplace.visualstudio.com/items?itemName=christian-kohler.path-intellisense)**: Autocompletes file paths.
- **[dooez.alt-catppuccin-vsc](https://marketplace.visualstudio.com/items?itemName=dooez.alt-catppuccin-vsc)**: Catppuccin color theme with alternative syntax styles.
- **[eamodio.gitlens](https://marketplace.visualstudio.com/items?itemName=eamodio.gitlens)**: Inline Git blame, file history, and repository views.
- **[github.copilot-chat](https://marketplace.visualstudio.com/items?itemName=github.copilot-chat)**: GitHub Copilot chat and agent mode.
- **[gruntfuggly.todo-tree](https://marketplace.visualstudio.com/items?itemName=gruntfuggly.todo-tree)**: Collects TODO and FIXME comments into a tree view.
- **[mechatroner.rainbow-csv](https://marketplace.visualstudio.com/items?itemName=mechatroner.rainbow-csv)**: Colors CSV columns and runs SQL-like queries on them.
- **[ms-python.debugpy](https://marketplace.visualstudio.com/items?itemName=ms-python.debugpy)**: Python debugger.
- **[ms-python.python](https://marketplace.visualstudio.com/items?itemName=ms-python.python)**: Python language support: running, testing, and linting.
- **[ms-python.vscode-pylance](https://marketplace.visualstudio.com/items?itemName=ms-python.vscode-pylance)**: Python language server with type checking and completions.
- **[ms-python.vscode-python-envs](https://marketplace.visualstudio.com/items?itemName=ms-python.vscode-python-envs)**: Creates and switches Python environments and their packages.
- **[pkief.material-icon-theme](https://marketplace.visualstudio.com/items?itemName=pkief.material-icon-theme)**: Material Design file and folder icons.
- **[shd101wyy.markdown-preview-enhanced](https://marketplace.visualstudio.com/items?itemName=shd101wyy.markdown-preview-enhanced)**: Markdown preview with diagrams, math, and export.
- **[streetsidesoftware.code-spell-checker](https://marketplace.visualstudio.com/items?itemName=streetsidesoftware.code-spell-checker)**: Spell checker that understands camelCase and other code identifiers.
- **[yzhang.markdown-all-in-one](https://marketplace.visualstudio.com/items?itemName=yzhang.markdown-all-in-one)**: Markdown shortcuts, tables of contents, and list editing.

## Global Python packages (uv)

- **[pre-commit](https://pre-commit.com/)**: Git hook manager. This repository's hook runs `scripts/check-docs.py` before each commit, and a chezmoi run file installs the hook.
- **[ruff](https://docs.astral.sh/ruff/)**: Python linter and formatter.

## Global Node packages (ni)

- **[skills](https://github.com/vercel-labs/skills)**: Finds and installs reusable agent skills. Tracks its latest version.

## JavaScript toolchain (mise)

- **[bun](https://bun.sh/docs)**: JavaScript runtime, bundler, and package manager.
- **[node](https://nodejs.org/docs)**: JavaScript runtime.
- **[pnpm](https://pnpm.io/)**: Package manager.
- **[yarn](https://yarnpkg.com/)**: Package manager for projects with a Yarn lockfile.

## Config files

- **[`~/.Brewfile`](https://docs.brew.sh/Brew-Bundle-and-Brewfile)**: Lists every Homebrew formula, cask, VS Code extension, and global Python package. A chezmoi run file installs from it whenever it changes.
- **[`~/.codex/AGENTS.md`](https://developers.openai.com/codex/guides/agents-md)**: Global instructions for Codex: keep tool discovery narrow and load only the tool schemas a task needs.
- **[`~/.config/chezmoi/chezmoi.toml`](https://www.chezmoi.io/reference/configuration-file/)**: chezmoi's own configuration, rendered from `.chezmoi.toml.tmpl` by `chezmoi init`. Records where the source checkout lives so later commands find it.
- **[`~/.config/gh/config.yml`](https://cli.github.com/manual/gh_config)**: GitHub CLI settings. Uses HTTPS for Git operations and defines the `co` alias for `gh pr checkout`.
- **[`~/.config/ghostty/config.ghostty`](https://ghostty.org/docs/config)**: Ghostty settings: Catppuccin Mocha theme, MonoLisa Variable at 14 pt, and the Nerd Font symbols as a fallback for icons.
- **[`~/.config/karabiner/karabiner.json`](https://karabiner-elements.pqrs.org/docs/)**: Karabiner-Elements key remaps. Caps Lock is Escape when tapped and Caps Lock when held, Fn plus a key sends Shift+Option+Control+Command plus that key, and Right Option is forward delete.
- **[`~/.config/linearmouse/linearmouse.json`](https://linearmouse.org/)**: LinearMouse settings. The BenQ ZOWIE mice get fixed pointer speeds without acceleration and reversed scrolling; the built-in trackpad keeps its scroll direction.
- **[`~/.config/mise/config.toml`](https://mise.jdx.dev/configuration.html)**: Selects node LTS and the latest pnpm, bun, and yarn, and lets node read a project's `.nvmrc` or `.node-version`.
- **[`~/.gitconfig`](https://git-scm.com/docs/git-config)**: Git identity and defaults: `main` as the first branch, rebase on pull with auto-stash, rerere, prune on fetch, `zdiff3` conflicts, moved-line coloring, and delta as a side-by-side pager. Defines the `lg` graph-log alias.
- **[`~/.nirc`](https://github.com/antfu-collective/ni)**: Makes pnpm ni's fallback for projects without a lockfile and its manager for global installs, so global Node packages work in every project.
- **[`~/.zprofile`](https://zsh.sourceforge.io/Doc/Release/Files.html)**: Login-shell setup. Loads Homebrew's environment so its commands are on `PATH`.
- **[`~/.zshenv`](https://zsh.sourceforge.io/Doc/Release/Files.html)**: Setup for every zsh. Puts the global Python packages (`~/.local/bin`) and the global Node packages (`~/Library/pnpm`) on `PATH`.
- **[`~/.zshrc`](https://zsh.sourceforge.io/Doc/Release/Files.html)**: Interactive-shell setup: nvim as `$EDITOR` and `$VISUAL`, TinyTeX on `PATH`, vi mode with `jj` to leave insert mode, fzf's key bindings and completion, zoxide, mise, starship, scmpuff, and the file, Git, and dotfiles aliases.

## Chezmoi run files

- **[run_once_install-fonts.sh](https://www.chezmoi.io/user-guide/use-scripts-to-perform-actions/)**: Installs the Nerd Font symbols cask and copies the MonoLisa files from `fonts/` to `~/Library/Fonts`. Runs once per machine.
- **[run_once_install-latex-pandoc.sh](https://www.chezmoi.io/user-guide/use-scripts-to-perform-actions/)**: Installs TinyTeX in `~/Library/TinyTeX`, the LaTeX packages that PDF output needs, and the Eisvogel pandoc template. Runs once per machine.
- **[run_once_macos-defaults.sh](https://www.chezmoi.io/user-guide/use-scripts-to-perform-actions/)**: Turns off press-and-hold in VS Code and Ghostty so held keys repeat for Vim motions. Runs once per machine.
- **[run_onchange_after_10-macos-keyboard.sh.tmpl](https://www.chezmoi.io/user-guide/use-scripts-to-perform-actions/)**: Turns off press-and-hold system-wide, so holding a key repeats it instead of opening the accent menu. macOS only.
- **[run_onchange_after_20-macos-finder.sh.tmpl](https://www.chezmoi.io/user-guide/use-scripts-to-perform-actions/)**: Finder preferences: full path in the title bar, path bar rooted at home, search the current folder, column view, hidden files shown, and no `.DS_Store` files on network shares. Restarts Finder. macOS only.
- **[run_onchange_after_30-install-packages.sh.tmpl](https://www.chezmoi.io/user-guide/use-scripts-to-perform-actions/)**: Installs the Brewfile with `brew bundle` without upgrading what is already installed, the JavaScript toolchain packages with mise, and the global Node packages with `ni -g`, and turns off Corepack's Yarn launcher so mise's Yarn runs instead. Reruns when the Brewfile, `~/.nirc`, the mise config, or the Node package list changes. macOS only.
- **[run_onchange_after_40-install-pre-commit-hook.sh.tmpl](https://www.chezmoi.io/user-guide/use-scripts-to-perform-actions/)**: Runs `pre-commit install` in the source checkout so commits run `scripts/check-docs.py`. Runs after the packages are installed. macOS only.
