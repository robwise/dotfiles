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
and document tools. Initialization alone does not apply dotfiles. The generated
chezmoi configuration is separate from the managed destination dotfiles.

## Run the skills CLI

Use pnpm to run the [skills CLI](https://github.com/vercel-labs/skills) on demand:

```sh
pnpm dlx skills@latest find
pnpm dlx skills@latest add owner/repo
```

Mise manages Node and pnpm. The skills CLI is run through `pnpm dlx` so it can
follow the publisher's `latest` release without a separate managed installation
or version pin. Pnpm caches `dlx` commands for one day by default, so repeated
invocations may reuse the downloaded version during that period. See the
[pnpm cache setting](https://pnpm.io/10.x/settings#dlxcachemaxage).
