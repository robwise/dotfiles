alias gpthis='git push origin $(git_current_branch) -u'
alias gcom='gco master'
alias ga.='git add .'
alias gcmh.='git add . && git commit --amend -C HEAD'
alias gmv='git mv'
alias grbm='git rebase master'
alias gclean='git clean -d -i'
alias grbc='git rebase --continue'
alias grba='git rebase --abort'
alias reb="gcom && gpl && gco - && grbm"

alias gitpurge="git checkout master && git remote update --prune | git branch -r --merged | grep -v master | sed -e 's/origin\//:/' | xargs git push origin"
alias branches="git branch -vv"

alias log="git log --pretty=format:'%C(auto)%h - %C(yellow)(%cr)%Creset %s <%an> %C(auto)%d' --graph"
alias hist="git log --pretty=format:\"%h %ad | %s%d [%an]\" --graph --date=short"
alias lg="git log --graph --pretty=format:'%Cred%h%Creset -%C(yellow)%d%Creset %s %Cgreen(%cr) %C(bold blue)<%an>%Creset' --abbrev-commit --date=relative"

# Override the default zsh one: https://github.com/robbyrussell/oh-my-zsh/blob/master/plugins/git/git.plugin.zsh
# so that --no-ff
alias gm='git merge --no-ff'

# gitignore.io API
function gi() { curl -L -s https://www.gitignore.io/api/\$@ ;}

alias git-diff-master-develop='git log --left-right --graph --cherry-pick master..develop'

# Version for typical branches off of master
alias git-cleanup-merged-branches='git branch --merged master | grep -v master | xargs git branch -d'

alias git-cleanup-origin='git remote prune origin'

git-branch-current() {
    printf "%s\n" $(git branch 2> /dev/null | grep -e ^* | tr -d "\* ")
}

# https://gist.github.com/590895
git-log-last-pushed-hash() {
    local currentBranch=$(git-branch-current);
    git log --format="%h" -n 1 origin/${currentBranch}
}

git-rebase-unpushed() {
    git rebase --interactive $(git-log-last-pushed-hash)
}

gitk_everything() {
    gitk --all --date-order $(git log -g --pretty=%H)
}

git-list-remote-branches-to-remove() {
    git branch -r --merged | grep 'origin/' | grep -v "origin/master$" | grep -v "origin/develop$" | sed 's/\s*origin\///'
}

git-list-remote-branches-to-remove-do-it() {
    git-list-remote-branches-to-remove | xargs -n 1 git push --delete origin
}

git-file-diffs() {
    git log -p $@
}
