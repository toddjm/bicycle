# Copyright 2011 bicycle trading llc

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

# specific environment for Linux OS
UNAME=`uname`
if [ "$UNAME" = "Linux" ]; then
    # add site-packages and  $BICYCLE_HOME/lib to PYTHONPATH
    PYTHONDIR="/usr/local/lib/python2.7/site-packages"
    if [ -d "$PYTHONDIR" ]; then
	export PYTHONPATH=$PYTHONDIR:$BICYCLE_HOME/lib
    fi
    # sets a color prompt if COLOR_PROMPT=yes
    case "$TERM" in
	xterm-color) COLOR_PROMPT=no;;
    esac
    # FORCE_COLOR_PROMPT=yes
    if [ -n "$FORCE_COLOR_PROMPT" ]; then
	if [ -x /usr/bin/tput ] && tput setaf 1 >&/dev/null; then
	    COLOR_PROMPT=yes
	else
	    COLOR_PROMPT=
	fi
    fi
    # set PS1
    if [ "$COLOR_PROMPT" = yes ]; then
	PS1='\[\033[01;32m\]\u@\h\[\033[00m\]:\[\033[01;34m\]\w\[\033[00m\]\$ '
    else
	PS1='[\u@\h:\w]\n$ '
    fi
    unset COLOR_PROMPT FORCE_COLOR_PROMPT
    # if this is an xterm, set the window title to user@host: dir
    case "$TERM" in
	xterm*|rxvt*)
	    PS1="\[\e]0;\u@\h: \w\a\]$PS1"
	    ;;
	*)
	    ;;
    esac
    # enable color support for ls
    if [ -x /usr/bin/dircolors ]; then
	test -r ~/.dircolors && eval "$(dircolors -b ~/.dircolors)" || eval "$(dircolors -b)"
    fi
fi
unset PYTHONDIR UNAME

# don't duplicate lines in history, see bash(1) for more options
HISTCONTROL=ignoredups:ignorespace

# set history length, see bash(1)
HISTSIZE=1000
HISTFILESIZE=2000

# append history
if [ -n "$PROMPT_COMMAND" ]; then
    PROMPT_COMMAND="$PROMPT_COMMAND; history -a"
else
    PROMPT_COMMAND='history -a'
fi

# alias definitions
if [ -f ~/.bash_aliases ]; then
    . ~/.bash_aliases
fi
