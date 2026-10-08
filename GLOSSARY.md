# Dotfiles

Personal macOS machine setup, reproduced on a new computer by applying this
repository with chezmoi.

## Language

**Package**:
One entry that a package manager installs: a Homebrew formula or cask, a VS
Code extension, a global Python or Node package, or a mise-managed tool.
_Avoid_: Application, command line utility, tool

**Alias**:
A short name you type in place of a longer command, whether it is defined as a
shell alias, a shell function, a git alias, or a gh alias.
_Avoid_: Shortcut, function

**Key remap**:
A rule that changes what a physical key or key combination does.
_Avoid_: Keybinding, shortcut, modification

**Config file**:
A file chezmoi places in the home directory to configure a tool.
_Avoid_: Dotfile, settings file

**Chezmoi run file**:
A script chezmoi executes while applying the repository to change machine state.
_Avoid_: Setup script, install script, hook

**Docs drift**:
A part of the setup that the inventory or usage guide doesn't describe
correctly: missing, out of date, or describing something no longer in the
repository.
_Avoid_: Doc gap, stale docs, drift (unqualified)

**Destination drift**:
A change to this machine's setup made outside the repository since chezmoi
last applied it, such as a config file edited in place or a package installed
by hand.
_Avoid_: Local changes, out of sync, drift (unqualified)

**Unapplied change**:
A change in the repository that hasn't yet been applied to this machine. It is
not drift, and `chezmoi apply` resolves it.
_Avoid_: Pending drift, source drift
