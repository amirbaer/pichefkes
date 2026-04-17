export PAGER="less -R"
export EDITOR="vim"
  
export HISTSIZE=10000
export HISTFILESIZE=10000
export HISTCONTROL="ignoredups"
shopt -s histappend

export CLICOLOR=1
export LSCOLORS="Exgxcxdxcxegedabagacad"

__git_branch() { git branch 2>/dev/null | sed -n 's/^\* \(.*\)/ (\1)/p'; }
export PS1='\[\033[32m\][\[\033[00m\] \u@\h:\[\033[34m\]\w\[\033[33m\]$(__git_branch) \[\033[32m\]]\[\033[00m\] '

alias less="less -R"

alias jq="jq -C"
function jctl () { cat $1 | jq | less ; }
function jctlip () { local tmp=$(mktemp) && sed 's/\x1b\[[0-9;]*m//g' "$1" | command jq . > "$tmp" && mv "$tmp" "$1"; }
function mem() { ps -eo rss,pid,euser,args:100 --sort %mem | grep -v grep | grep -i $@ | awk '{printf $1/1024 "MB"; $1=""; print }'; }

