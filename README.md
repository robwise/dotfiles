# Dotfiles

Personal macOS dotfiles managed with [chezmoi](https://www.chezmoi.io/).
Choose where to keep the source checkout when initializing chezmoi.

## Set up a new machine

With chezmoi installed and SSH access to the repository, set `DOTFILES_SOURCE`
to your preferred absolute path. The path below is an example:

```sh
DOTFILES_SOURCE="$HOME/dev/projects/dotfiles"
mkdir -p "$(dirname "$DOTFILES_SOURCE")"
chezmoi init --source "$DOTFILES_SOURCE" git@github.com:robwise/dotfiles.git
chezmoi source-path
```

The source-path command should print the location you selected in
`DOTFILES_SOURCE`. `--source` tells chezmoi where to clone before it can
read the configuration template. The root `.chezmoi.toml.tmpl` remembers the
selected location in chezmoi's local configuration for subsequent commands.

Review the proposed changes:

```sh
chezmoi diff
```

Then apply them when ready:

```sh
chezmoi apply
```

Applying also runs eligible setup scripts, including macOS preferences, fonts,
document tools, Brewfile packages, and global Node packages. Initialization alone
does not apply dotfiles. The generated chezmoi configuration is separate from
the managed destination dotfiles.

## Use the project's package manager

[ni](https://github.com/antfu-collective/ni) detects a project's package manager
from its metadata and lockfiles, then runs the corresponding command. We keep
fallback and global package-manager choices in `.nirc`. Mise manages Node, pnpm,
Bun, and Yarn.

## Run the skills CLI

The [skills CLI](https://github.com/vercel-labs/skills) finds and installs reusable
agent skills. Chezmoi installs it globally through `ni` using the package manager
selected in `.nirc`, so `skills` is available across projects.

## Codex skill settings

[Codex](https://developers.openai.com/codex/) provides the coding agent and its
configuration writer. Chezmoi installs the pinned CLI through `ni` and applies
individual disables for the personal ChatGPT skills on each apply. The explicit
skills publisher updates `.chezmoidata/codex-skill-disables.json` from committed
agent declarations; removed selectors stop being enforced without being enabled.
