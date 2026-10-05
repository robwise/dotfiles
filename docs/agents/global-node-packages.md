# Global Node packages

Record persistent global Node CLI packages in `packages.node` in
`.chezmoidata/packages.toml`, then apply through chezmoi using
`run_onchange_after_30-install-packages.sh.tmpl`.

Route global installs through `ni -g`. Treat `globalAgent` in `dot_nirc` (deployed
as `~/.nirc`) as the single source of truth; derive manager-specific behavior
from that setting instead of hardcoding a package manager elsewhere.
