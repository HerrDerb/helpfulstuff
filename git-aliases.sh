# deletes all merged branches https://stackoverflow.com/questions/13064613/how-to-prune-local-tracking-branches-that-do-not-exist-on-remote-anymore
alias git-clean='git fetch --prune && git branch -r | awk "{print \$1}" | egrep -v -f /dev/fd/0 <(git branch -vv | grep origin) | awk "{print \$1}" | xargs git branch -D'
# fix and rebase a past commit
function git-fixup { git commit --fixup HEAD~$1 && git rebase -i --autosquash HEAD~$(( $1 + 2 )); }
export -f git-fixup