# Copyright 2011, 2012 bicycle trading, llc

if [[ -n $BASH_VERSION ]]
then
  if [[ -f ~/.bashrc ]]
  then
    . ~/.bashrc
  fi
fi

if [[ -d ~/bin ]]
then
  export PATH=~/bin:$PATH
fi
