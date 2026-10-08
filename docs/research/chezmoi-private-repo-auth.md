# chezmoi with a private repo: authentication on a fresh Mac

Research date: 2026-10-06. Question: what does chezmoi recommend for a private
dotfiles repo, and what is the least-manual way to authenticate when setting up
`github.com/robwise/dotfiles` on a fresh macOS install, without installing
Homebrew or `gh` by hand?

Sections 1 to 5 are cited facts. Section 6 is the recommendation, which draws on
those facts. Claims are marked **(unverified)** where they are inferred, or were
not tested on a fresh Mac.

Pinned source revisions used for code citations:

- chezmoi `5b685d863fd55f7ac10ba3ab417d6a1df7dd0220` (master, 2026-10-06), shortened below to `CZ`, which stands for
  `https://github.com/twpayne/chezmoi/blob/5b685d863fd55f7ac10ba3ab417d6a1df7dd0220`
- GitHub CLI `17142e08db2e300b37e6da1ddcfb651eb6d9c587`, shortened to `GH`, which stands for
  `https://github.com/cli/cli/blob/17142e08db2e300b37e6da1ddcfb651eb6d9c587`
- Apple Git `6b2f9bfe72d6d4b5c9bcc1c2d0236c026d321cba` (Git-155), shortened to `AG`, which stands for
  `https://github.com/apple-oss-distributions/Git/blob/6b2f9bfe72d6d4b5c9bcc1c2d0236c026d321cba`
- Homebrew git formula `e1bf4ad24ef239c2e7a2078884cad9c8cbcc31bf`, shortened to `HB`, which stands for
  `https://github.com/Homebrew/homebrew-core/blob/e1bf4ad24ef239c2e7a2078884cad9c8cbcc31bf/Formula/g/git.rb`
- Homebrew installer `35da6871c4be7d7fdab2fd505fb7fa667926a2a5`, shortened to `HI`, which stands for
  `https://github.com/Homebrew/install/blob/35da6871c4be7d7fdab2fd505fb7fa667926a2a5/install.sh`

## 1. chezmoi's position on public and private repos

- chezmoi supports both public and private repos. It is designed so that the
  repo *can* be public, by keeping secrets in a password manager, in encrypted
  files, or in private configuration files. "Your dotfiles repo can still be
  private, if you choose."
  [Setup guide, private repo section](https://www.chezmoi.io/user-guide/setup/#use-a-private-repo-to-store-your-dotfiles)
- With a private repo, "you will typically need to enter your credentials ...
  each time you interact with the repo". "chezmoi itself does not store any
  credentials, but instead relies on your local git configuration for these
  operations." (same source)
- On GitHub without `--ssh`, the password prompt takes a GitHub personal access
  token (PAT). (same source)
- The quick start's "Private GitHub repos require other authentication methods"
  hint shows an SSH URL (`git@github.com:$GITHUB_USERNAME/dotfiles.git`) for
  both `chezmoi init` and `chezmoi init --apply`. Its link points to GitHub's
  "Cloning with HTTPS URLs" page.
  [Quick start](https://www.chezmoi.io/quick-start/)
- The install page gives the same SSH-URL hint for the one-line installer:
  `sh -c "$(curl -fsLS https://get.chezmoi.io)" -- init --apply git@github.com:$GITHUB_USERNAME/dotfiles.git`.
  [Install, one-line binary install](https://www.chezmoi.io/install/#one-line-binary-install)
- The FAQ pages (general, design, usage, troubleshooting) do not discuss public
  versus private repos. The only discussion is in the setup guide.
  [FAQ: general](https://www.chezmoi.io/user-guide/frequently-asked-questions/general/),
  [design](https://www.chezmoi.io/user-guide/frequently-asked-questions/design/)

**Why:** chezmoi's stated reason is that its secret-management features make a
public repo safe. It treats privacy as the user's choice, and leaves
authentication entirely to git.

## 2. Authentication methods for a private repo, and what each needs on a bare machine

chezmoi's own docs name only two methods: SSH (`--ssh` or an SSH URL), and HTTPS
with a PAT typed at the password prompt (sources in section 1). The rest of this
section uses GitHub's and git's docs.

### What a bare Mac has

- On a fresh macOS install, invoking a Command Line Tools (CLT) command such as
  `git` "prompts you to download and install the Command Line Tools for Xcode
  package". `xcode-select --install` opens the same system dialog.
  [Apple: Installing the command-line tools](https://developer.apple.com/documentation/xcode/installing-the-command-line-tools)
- This means `/usr/bin/git` exists before the CLT do, as a launcher that
  triggers that prompt. That is an inference from Apple's wording. On this
  machine, `/usr/bin/git` is a 119 KB binary and the real git lives under
  `/Library/Developer/CommandLineTools` (observed locally). **(unverified on a
  fresh Mac)**
- `curl` and `/usr/bin/ssh-keygen` are part of the base system (observed
  locally). chezmoi's installer needs only `curl` or `wget`.
  [Install](https://www.chezmoi.io/install/#one-line-binary-install)

### Methods

| Method | What GitHub says | Needs on a bare Mac |
| --- | --- | --- |
| HTTPS + fine-grained PAT | Recommended over classic PATs. Can be limited to selected repositories. Clone needs **Contents: read**, push needs **Contents: write**. Has an expiration ("infinite" lifetimes allowed unless policy blocks them). Typed as the password at git's `Username:` and `Password:` prompt. [Managing PATs](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens) | A browser to create the token. Either chezmoi's built-in git (section 3) or the CLT's git. |
| HTTPS + classic PAT | Grants access to all repositories you can reach. Unused tokens are removed after a year. (same source) | Same as above. Broader blast radius. |
| SSH key on your account | Generate with `ssh-keygen -t ed25519`. Add to the agent with `ssh-add --apple-use-keychain`. Then add the public key to your GitHub account. [Generating a new SSH key](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent), [Adding a key](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/adding-a-new-ssh-key-to-your-github-account) | Real git (the CLT), because chezmoi's built-in git refuses SSH (section 3). A browser, or an already-authenticated `gh`, to upload the key. |
| Deploy key (SSH) | Grants access to a single repository. Read-only by default, write optional. Usually no passphrase, and no expiry. GitHub recommends a GitHub App instead. [Managing deploy keys](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/managing-deploy-keys) | Same as an SSH key: the CLT plus a browser. It is meant for servers, so it is a poor fit for a personal laptop. |
| `gh auth login` (HTTPS) | Web browser flow. The token is stored in the system credential store, falling back to a plain-text file. Choosing HTTPS and answering yes to "Authenticate Git with your GitHub credentials?" stores git credentials. [gh auth login](https://cli.github.com/manual/gh_auth_login), [Caching credentials](https://docs.github.com/en/get-started/git-basics/caching-your-github-credentials-in-git), [`GH/pkg/cmd/auth/shared/git_credential.go#L41`](https://github.com/cli/cli/blob/17142e08db2e300b37e6da1ddcfb651eb6d9c587/pkg/cmd/auth/shared/git_credential.go#L41) | `gh` installed, which in practice means Homebrew first. That is what the owner wants to avoid. |
| Git Credential Manager | Stores credentials and handles OAuth, so you don't make a PAT. Installed via Homebrew on macOS. [Caching credentials](https://docs.github.com/en/get-started/git-basics/caching-your-github-credentials-in-git) | Homebrew first. |

### `gh auth setup-git` conflicts with a managed `~/.gitconfig`

- `gh auth setup-git` "configures git to use GitHub CLI as a credential helper".
  [gh auth setup-git](https://cli.github.com/manual/gh_auth_setup-git)
- It writes with `git config --global`. First it runs
  `--replace-all credential.https://github.com.helper ""`, which severs the
  helper chain. Then it runs `--add ... "!<gh path> auth git-credential"`.
  [`GH/.../helper_config.go#L41-L57`](https://github.com/cli/cli/blob/17142e08db2e300b37e6da1ddcfb651eb6d9c587/pkg/cmd/auth/shared/gitcredentials/helper_config.go#L41-L57),
  [`keyFor` at L114-L117](https://github.com/cli/cli/blob/17142e08db2e300b37e6da1ddcfb651eb6d9c587/pkg/cmd/auth/shared/gitcredentials/helper_config.go#L114-L117)
- `--global` writes go to `~/.gitconfig`. This repo manages that file
  (`dot_gitconfig`), and `dot_gitconfig` sets no `credential` section. So the
  next `chezmoi apply` removes gh's helper, possibly after asking before it
  overwrites the changed file. That is an inference from the code
  above plus the repo contents. **(unverified by test)** After that, git falls
  back to the osxkeychain helper (section 4). That helper holds nothing for
  github.com if the only sign-in so far was through gh, so git prompts.

## 3. chezmoi's built-in git (go-git): prompting and credential reuse

- `useBuiltinGit` defaults to `auto`, documented as "Use builtin git if `git`
  command is not found in `$PATH`."
  [Config variables](https://www.chezmoi.io/reference/configuration-file/variables/)
  The `auto` check is only `LookPath(git.command)`.
  [`CZ/internal/cmd/config.go#L3135-L3141`](https://github.com/twpayne/chezmoi/blob/5b685d863fd55f7ac10ba3ab417d6a1df7dd0220/internal/cmd/config.go#L3135-L3141)
  - **Consequence (unverified on a fresh Mac):** `/usr/bin/git` exists before
    the CLT do (section 2), so `auto` picks external git. The clone then hits
    Apple's install prompt instead of go-git. To use go-git on a bare Mac you
    must pass `--use-builtin-git true`. This matches the observed behaviour,
    where `--use-builtin-git true` led to go-git's `Username` prompt.
- Built-in clone over SSH is refused outright: "builtin git does not support
  cloning repos over ssh, please install git".
  [`CZ/internal/cmd/initcmd.go#L272-L279`](https://github.com/twpayne/chezmoi/blob/5b685d863fd55f7ac10ba3ab417d6a1df7dd0220/internal/cmd/initcmd.go#L272-L279)
- When the clone fails with `ErrAuthenticationRequired`, go-git prints the
  error, reads `Username?` and `Password?` (the password is not echoed), sets
  them as `http.BasicAuth` on that clone's options, and retries in a loop.
  [`CZ/internal/cmd/initcmd.go#L299-L322`](https://github.com/twpayne/chezmoi/blob/5b685d863fd55f7ac10ba3ab417d6a1df7dd0220/internal/cmd/initcmd.go#L299-L322)
  - The credentials live only in that in-memory `CloneOptions`. Nothing is
    written to a credential helper or the keychain, consistent with the docs'
    "chezmoi itself does not store any credentials"
    ([setup guide](https://www.chezmoi.io/user-guide/setup/#use-a-private-repo-to-store-your-dotfiles)).
  - The remote URL is saved as given, without the token. That is an inference
    from the code passing `URL` and `Auth` separately. **(unverified)**
- `chezmoi update` with built-in git calls `wt.Pull` with no `Auth`.
  [`CZ/internal/cmd/updatecmd.go#L60-L77`](https://github.com/twpayne/chezmoi/blob/5b685d863fd55f7ac10ba3ab417d6a1df7dd0220/internal/cmd/updatecmd.go#L60-L77)
  For a private HTTPS repo this would fail with an authentication error rather
  than prompt. That is inferred from source. **(unverified)** When real git is
  on `PATH`, `update` runs `git pull --autostash --rebase` instead.
  [update reference](https://www.chezmoi.io/reference/commands/update/)
- Push never uses go-git. `chezmoi git ...` runs `git.command`
  ([`CZ/internal/cmd/gitcmd.go#L36-L38`](https://github.com/twpayne/chezmoi/blob/5b685d863fd55f7ac10ba3ab417d6a1df7dd0220/internal/cmd/gitcmd.go#L36-L38)),
  and auto-push runs `git push` through `git.command`
  ([`CZ/internal/cmd/config.go#L1882`](https://github.com/twpayne/chezmoi/blob/5b685d863fd55f7ac10ba3ab417d6a1df7dd0220/internal/cmd/config.go#L1882)).
- **Conclusion:** go-git is a bootstrap-only path. After it, every pull and
  push goes through real git and that git's credential helper. The PAT has to
  be entered again the first time real git talks to GitHub.

### Repo URL guessing: the docs and the source disagree

- The `init` reference's table says `user/repo` guesses
  `https://user@github.com/user/repo.git`.
  [init reference](https://www.chezmoi.io/reference/commands/init/)
- The source at `CZ` guesses `https://github.com/$1/$2.git`, with no username.
  [`CZ/internal/cmd/initcmd.go#L38-L71`](https://github.com/twpayne/chezmoi/blob/5b685d863fd55f7ac10ba3ab417d6a1df7dd0220/internal/cmd/initcmd.go#L38-L71)
- Either way, git prompts for the username unless it is in the URL. Passing
  `https://robwise@github.com/robwise/dotfiles.git` explicitly would leave only
  the password prompt for external git. **(unverified)** go-git always asks
  for both.

## 4. macOS git already configures osxkeychain, outside `~/.gitconfig`

- Apple's git build installs a `gitconfig` containing
  `[credential] helper = osxkeychain` and `[init] defaultBranch = main` into
  `$(PREFIX)/share/git-core`.
  [`AG/gitconfig`](https://github.com/apple-oss-distributions/Git/blob/6b2f9bfe72d6d4b5c9bcc1c2d0236c026d321cba/gitconfig),
  [`AG/Makefile#L149`](https://github.com/apple-oss-distributions/Git/blob/6b2f9bfe72d6d4b5c9bcc1c2d0236c026d321cba/Makefile#L149)
- Apple patched `config.c` to read that file at its own `CONFIG_SCOPE_XCODE`.
  It reads it *before* `/etc/gitconfig` (system) and before
  `~/.gitconfig` (global). It is skipped only when `GIT_CONFIG_NOSYSTEM` is set.
  [`AG/src/git/config.c#L2016-L2058`](https://github.com/apple-oss-distributions/Git/blob/6b2f9bfe72d6d4b5c9bcc1c2d0236c026d321cba/src/git/config.c#L2016-L2058)
- Local observation on this Mac, with CLT 26.6 and `git version 2.50.1 (Apple Git-155)`:
  `/usr/bin/git config --show-scope --show-origin -l`, run with an empty
  `HOME`, still reports
  `unknown file:/Library/Developer/CommandLineTools/usr/share/git-core/gitconfig credential.helper=osxkeychain`.
  `git-credential-osxkeychain` is present in
  `/Library/Developer/CommandLineTools/usr/libexec/git-core/`.
- Homebrew's git formula also builds `git-credential-osxkeychain` and installs
  `etc/gitconfig` with `helper = osxkeychain` on macOS. That is
  `/opt/homebrew/etc/gitconfig`, at system scope.
  [`HB#L135-L142`](https://github.com/Homebrew/homebrew-core/blob/e1bf4ad24ef239c2e7a2078884cad9c8cbcc31bf/Formula/g/git.rb#L135-L142),
  [`HB#L204-L210`](https://github.com/Homebrew/homebrew-core/blob/e1bf4ad24ef239c2e7a2078884cad9c8cbcc31bf/Formula/g/git.rb#L204-L210)
  The repo's Brewfile installs `git`, so both gits end up configured.
- git consults helpers in order and stops once it has a username and password.
  An empty `credential.helper` value resets the list. With no helper at all,
  git prompts on the terminal every time.
  [gitcredentials](https://git-scm.com/docs/gitcredentials)
- **Consequence:** a managed `~/.gitconfig` that never sets `credential.helper`
  leaves osxkeychain active for both Apple's and Homebrew's git. The first
  successful HTTPS auth with real git is saved to the login keychain, and later
  pulls and pushes reuse it.
- Two open points. **(unverified)**
  - Whether Apple's and Homebrew's helper binaries share the keychain item
    without a macOS access prompt.
  - Exactly when an expired PAT is erased from the keychain and the prompt
    comes back.

## 5. Installing prerequisites such as Homebrew before other scripts

### `run_once_before_` and `run_onchange_before_` scripts

- Scripts run in alphabetical order. `before_` scripts run before files are
  updated. `run_once_` scripts run once per unique content hash (computed after
  template execution). Scripts should be idempotent. Templates that render to
  whitespace are skipped.
  [Use scripts to perform actions](https://www.chezmoi.io/user-guide/use-scripts-to-perform-actions/)
- FAQ, "How do I install pre-requisites for templates?": use a `run_before`
  script that is **not** a template. "chezmoi will make sure to execute it
  before templating other files."
  [FAQ: usage](https://www.chezmoi.io/user-guide/frequently-asked-questions/usage/#how-do-i-install-pre-requisites-for-templates)
- The macOS guide shows `run_onchange_before_install-packages-darwin.sh.tmpl`
  running `brew bundle`. It assumes `brew` already exists.
  [macOS guide](https://www.chezmoi.io/user-guide/machines/macos/)
- Scripts inherit chezmoi's stdin.
  [`CZ/internal/chezmoi/realsystem.go#L193`](https://github.com/twpayne/chezmoi/blob/5b685d863fd55f7ac10ba3ab417d6a1df7dd0220/internal/chezmoi/realsystem.go#L193)
  So an interactive `chezmoi init --apply` gives the Homebrew installer a TTY
  for its sudo prompt. The installer switches to non-interactive mode only when
  stdin is not a TTY, or when `CI` or `NONINTERACTIVE` is set.
  [`HI#L125-L147`](https://github.com/Homebrew/install/blob/35da6871c4be7d7fdab2fd505fb7fa667926a2a5/install.sh#L125-L147)
- The Homebrew installer installs the CLT itself when
  `/Library/Developer/CommandLineTools/usr/bin/git` is missing and it has sudo.
  It tries a headless `softwareupdate -i` first, then falls back to the
  `xcode-select --install` GUI.
  [`HI#L446-L453`](https://github.com/Homebrew/install/blob/35da6871c4be7d7fdab2fd505fb7fa667926a2a5/install.sh#L446-L453),
  [`HI#L885-L921`](https://github.com/Homebrew/install/blob/35da6871c4be7d7fdab2fd505fb7fa667926a2a5/install.sh#L885-L921)
  Homebrew's docs list the CLT as a requirement for building from source, and
  `NONINTERACTIVE=1` for unattended installs.
  [Homebrew installation](https://docs.brew.sh/Installation)
- Caveat for this repo: the pending (untracked) `run_once_before_00-install-homebrew.sh.tmpl`
  is a template, which goes against the FAQ's "not a template" advice. That
  advice matters when other templates call a tool the script installs. Today
  the repo's `.tmpl` files use only `include`, `sha256sum`, `shellQuoteList`,
  `join`, and `.chezmoi.*` data. A grep for `output`, `lookPath`,
  `onepassword`, and `gitHub` found no template-time tool calls. The only hit
  was `mise exec` in a script *body*, which runs at script time. So the
  template form is harmless for now.

### `hooks.read-source-state.pre`

- Runs after `chezmoi init` has cloned the repo but before the source state is
  read. The docs suggest it for installing a password manager. Caveats from the
  docs:
  - It runs on every command that reads the source state, so it must exit
    quickly when there is nothing to do.
  - It is not a template.
  - It is configured in the config file (`[hooks.read-source-state.pre]`).
  [Install your password manager on init](https://www.chezmoi.io/user-guide/advanced/install-your-password-manager-on-init/)
- Hooks always run, even with `--dry-run`, and should be fast and idempotent.
  [Hooks reference](https://www.chezmoi.io/reference/configuration-file/hooks/)
- Hook commands run with the home directory as the working directory.
  [`CZ/internal/cmd/config.go#L2785-L2807`](https://github.com/twpayne/chezmoi/blob/5b685d863fd55f7ac10ba3ab417d6a1df7dd0220/internal/cmd/config.go#L2785-L2807)
  - The docs' relative path `.local/share/chezmoi/...` is therefore wrong for
    this repo's custom `--source`.
  - Write the path as `{{ .chezmoi.sourceDir }}/...` in `.chezmoi.toml.tmpl`.
- On a fresh machine the hook exists only after `init` has generated the config
  from `.chezmoi.toml.tmpl`. `init` reloads the config before `--apply`
  ([`CZ/internal/cmd/initcmd.go#L218-L245`](https://github.com/twpayne/chezmoi/blob/5b685d863fd55f7ac10ba3ab417d6a1df7dd0220/internal/cmd/initcmd.go#L218-L245)),
  so the hook should fire during the first `init --apply`. **(unverified by
  test)**
- Neither mechanism helps with authentication or the clone. Both live in the
  repo, so they run only after the clone has already succeeded.

## 6. Recommendation for this repo

This section is analysis, not a cited fact.

### The constraint that drives the choice

Until the repo is cloned, nothing in it can run. The clone itself must therefore
be done by one of two tools:

- **go-git:** needs `--use-builtin-git true`, HTTPS, and a PAT.
- **Real git:** needs the CLT first.

After the clone, `run_once_before_00-install-homebrew` can install the CLT (if
still missing), Homebrew, and then everything in the Brewfile, including `gh`.
For later pulls and pushes, Apple's built-in osxkeychain helper is the one
credential store that survives the managed `~/.gitconfig` with no repo changes.

### What Flows A and B assume about the repo

Both flows assume `run_once_before_00-install-homebrew.sh.tmpl` is committed.
At the time of writing it is untracked, so a fresh clone would not contain it.

A grep of the repo's run files shows what else depends on `brew`.
`run_once_install-fonts.sh` calls `brew install --cask` directly.
`run_onchange_after_30-install-packages.sh.tmpl` runs `brew bundle`. Two
ordering risks follow on a fresh machine. Both are inferred from the
[scripts docs](https://www.chezmoi.io/user-guide/use-scripts-to-perform-actions/)
and are **unverified by test**:

- **Fonts script may not find `brew`.** `run_once_install-fonts.sh` has no
  `before_` or `after_` attribute, so it runs during the file updates. It does
  not add `/opt/homebrew/bin` to `PATH`. A brand-new shell has no
  `/opt/homebrew/bin` on `PATH`, and chezmoi passes that environment to its
  scripts, so this script may fail to find `brew` even after the Homebrew
  script succeeds.
- **LaTeX script runs before its tools exist.**
  `run_once_install-latex-pandoc.sh` needs `tlmgr`. It runs during the file
  updates, before the `after_30` script installs Brewfile packages.

These are outside the authentication question but would break a one-command
`init --apply`.

### Flow A (recommended): CLT first, then one chezmoi command, HTTPS with a fine-grained PAT

1. In a browser, create a fine-grained PAT. Set the resource owner to
   `robwise`, choose "Only select repositories" with `robwise/dotfiles`, grant
   Contents: read and write, and set an expiration.
2. Run `xcode-select --install`, then click Install in the dialog.
3. Run:

   ```sh
   sh -c "$(curl -fsLS https://get.chezmoi.io)" -- -b "$HOME/.local/bin" \
     init --apply --source "$HOME/dev/projects/dotfiles" \
     https://github.com/robwise/dotfiles.git
   ```

   - At git's `Username:` prompt, enter `robwise`. At `Password:`, paste the
     PAT.
   - The CLT's osxkeychain helper stores the PAT.
   - `--apply` then runs the Homebrew `run_once_before_` script. It asks for
     the sudo password, and the CLT are already present.
   - After that the Brewfile installs `chezmoi`, `git`, and `gh`.
   - The `-b` path is just a writable location for this first binary. The
     installer does not edit `PATH`
     ([install](https://www.chezmoi.io/install/#one-line-binary-install)), and
     the Brewfile's chezmoi replaces it afterwards.

- **Later pulls and pushes:** `chezmoi update` and `git push` from the source
  checkout use real git. The osxkeychain helper supplies the stored PAT with no
  prompt until it expires. Then git prompts once and stores the new token.
  Whether Homebrew's git reads the same keychain item without a prompt is
  **unverified**.
- **Manual steps:** create the PAT, click one CLT dialog, run one command, and
  answer the username, PAT, and sudo prompts. No Homebrew or `gh` by hand.
- **Trade-offs:**
  - A PAT has to be created and rotated.
  - The PAT is limited to this one repo, so it is a narrow credential.
  - This is the most fully documented path: chezmoi's
    [setup guide](https://www.chezmoi.io/user-guide/setup/#use-a-private-repo-to-store-your-dotfiles),
    GitHub's PAT docs, and Apple's config.

### Flow B: no CLT up front, using go-git

1. Create the PAT as in Flow A.
2. Run:

   ```sh
   sh -c "$(curl -fsLS https://get.chezmoi.io)" -- -b "$HOME/.local/bin" \
     --use-builtin-git true init --apply --source "$HOME/dev/projects/dotfiles" \
     https://github.com/robwise/dotfiles.git
   ```

   Answer go-git's `Username?` and `Password?` prompts. The Homebrew script
   then installs the CLT headlessly, plus Homebrew.

- **Later pulls and pushes:** go-git stored nothing. The first real-git pull or
  push therefore prompts for the PAT a **second** time, and osxkeychain stores
  it from then on.
- **Trade-offs:**
  - Skips the CLT dialog, at the cost of a second PAT entry.
  - Relies on inferences from source that were not tested on a fresh Mac:
    `auto` picking `/usr/bin/git`, and go-git persisting nothing.
- Whether the CLT dialog or a second paste is worse is a matter of taste. Both
  flows avoid Homebrew and `gh` by hand.

### Flow C: SSH

- Needs the CLT first, because go-git refuses SSH. It also needs
  `ssh-keygen`, an `~/.ssh/config` entry, and uploading the public key to
  GitHub in a browser.
- Pulls and pushes then use the key, through the agent and Keychain via
  `UseKeychain`.
- It has more manual steps than Flow A, and the key has no expiry.
- This Mac's checkout uses an SSH origin (`git@github.com:robwise/dotfiles.git`),
  while the managed `gh` config sets `git_protocol: https`. Pick one protocol
  and document it.
- A deploy key is the same mechanism, limited to this one repo. GitHub steers
  laptop users away from deploy keys.

### Options to avoid, or to adopt only after bootstrap

- **`gh auth login` plus `gh auth setup-git` before cloning** (the current
  README). This needs Homebrew and `gh` first. Its global helper entry is also
  wiped by the next `chezmoi apply` of `dot_gitconfig` (section 2).
- **To make `gh` the long-term helper:** manage the helper in `dot_gitconfig`
  itself. Add a `[credential "https://github.com"]` block with `helper =`
  followed by `helper = !/opt/homebrew/bin/gh auth git-credential`, mirroring
  what `gh auth setup-git` writes. Then apply cannot erase it.
  - How git behaves before `gh` exists, or before `gh auth login`, is
    **unverified**.
  - It adds a `gh auth login` step.
  - Flow A's osxkeychain already covers pulls and pushes without it.
- **Embedding the token in the clone URL:** none of the sources recommend it,
  and git would persist the token in `.git/config`. Not covered further.

### Bottom line

Flow A is the simplest documented path. It needs one CLT click, one
`get.chezmoi.io` command, and a repo-scoped fine-grained PAT entered once. The
Homebrew `run_once_before_` script installs everything else. Apple's
`osxkeychain` helper sits outside `~/.gitconfig`, so pulls and pushes keep
working after apply.
