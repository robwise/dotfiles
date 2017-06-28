bindkey -v
bindkey '^[[A' up-line-or-search
bindkey '^[[B' down-line-or-search
bindkey '^R' history-incremental-search-backward
bindkey '^F' history-incremental-search-forward
bindkey "\e[3~" delete-char
bindkey " " magic-space # do history expansion on space
bindkey "^G" history-search-backward
bindkey "^S" history-search-forward
bindkey '[C' forward-word
bindkey '[D' backward-word

# Order matters
source "$HOME/.yadm/scripts/init-vars.zsh"
source "$HOME/.yadm/scripts/aliases.zsh"
source "$HOME/.yadm/scripts/rails.zsh"
source "$HOME/.yadm/scripts/git.zsh"
source "$HOME/.yadm/scripts/git-flow.zsh"
source "$HOME/.yadm/scripts/personal-aliases.zsh"
