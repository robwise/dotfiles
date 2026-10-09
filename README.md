# Dotfiles

Personal macOS dotfiles managed with [chezmoi](https://www.chezmoi.io/).
Choose where to keep the source checkout when initializing chezmoi.

## Set up a new machine

Run chezmoi's one-line installer. It installs chezmoi into `~/.local/bin`,
clones this repository into the source checkout, and applies it:

```sh
sh -c "$(curl -fsLS https://get.chezmoi.io)" -- -b "$HOME/.local/bin" \
  init --apply --source "$HOME/dev/projects/dotfiles" robwise
```

`robwise` expands to `https://github.com/robwise/dotfiles.git`. `--source`
picks where the source checkout lives; change the path if you want it
elsewhere. The root `.chezmoi.toml.tmpl` remembers that location for later
chezmoi commands. To review before anything changes, leave out `--apply`,
then run `chezmoi diff` and `chezmoi apply`.

Applying writes the config files and runs the chezmoi run files, which set
macOS preferences and install fonts, Brewfile packages, global Node packages,
and TinyTeX with its LaTeX packages and the pandoc template. TinyTeX installs
in your home folder, so it never asks for a password. Initialization alone
does not apply anything. The generated chezmoi configuration is separate from
the config files chezmoi manages.

## Documentation

- [Inventory](docs/inventory.md): every package, font, config file, and chezmoi
  run file, with its purpose and our approach.
- [Usage](docs/usage.md): how to use the setup day to day, by activity,
  including every alias and key remap.
