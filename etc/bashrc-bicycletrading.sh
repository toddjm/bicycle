# Copyright 2011, 2012 bicycle trading llc

# use vi on the command line
set -o vi

# set environment variables - general
export EDITOR=vi
export GIT_EDITOR=vi
export LC_ALL=C
export SVN_EDITOR=vi

# set environment variables - specific
export BICYCLE_HOME=$HOME/bicycletrading
export TICKS_HOME=$HOME/bicycleticks
export PATH=$PATH:$BICYCLE_HOME/bin

# add site-packages and $BICYCLE_HOME/lib to PYTHONPATH
PYTHONDIR="/usr/local/lib/python2.7/site-packages"
if [[ -d $PYTHONDIR ]]
then
  export PYTHONPATH=$PYTHONDIR:$BICYCLE_HOME/lib
fi
unset PYTHONDIR
# prompt-related
case $TERM in
  xterm-color)
    COLOR_PROMPT=no
    ;;
esac
if [[ -n $FORCE_COLOR_PROMPT ]]
then
  if [[ -x /usr/bin/tput ]] && tput setaf 1 >&/dev/null
  then
    COLOR_PROMPT=yes
  else
    COLOR_PROMPT=
  fi
fi
if [[ $COLOR_PROMPT = yes ]]
then
  PS1='\[\033[01;32m\]\u@\h\[\033[00m\]:\[\033[01;34m\]\w\[\033[00m\]\$ '
else
  PS1='[\u@\h:\w]\n$ '
fi
unset COLOR_PROMPT FORCE_COLOR_PROMPT
case $TERM in
  xterm*|rxvt*)
    PS1="\[\e]0;\u@\h: \w\a\]$PS1"
    ;;
  *)
  ;;
esac
if [[ -x /usr/bin/dircolors ]]
then
  test -r ~/.dircolors && eval $(dircolors -b ~/.dircolors) || eval $(dircolors -b)
fi

# history-related
HISTCONTROL=ignoredups:ignorespace
HISTSIZE=1000
HISTFILESIZE=2000
if [[ -n $PROMPT_COMMAND ]]
then
  PROMPT_COMMAND="$PROMPT_COMMAND; history -a"
else
  PROMPT_COMMAND='history -a'
fi

# alias-related
if [[ -f ~/.bash_aliases ]]
then
  . ~/.bash_aliases
fi
