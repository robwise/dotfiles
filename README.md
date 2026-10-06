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

Applying writes the config files and runs the chezmoi run files, which set
macOS preferences and install fonts, TinyTeX and the pandoc template, Brewfile
packages, global Node packages, and this repository's pre-commit hook. Initialization alone
does not apply anything. The generated chezmoi configuration is separate from
the config files chezmoi manages.

## Documentation

- [Inventory](docs/inventory.md): every package, font, config file, and chezmoi
  run file, with its purpose and our approach.
- [Usage](docs/usage.md): how to use the setup day to day, by activity,
  including every alias and key remap.
