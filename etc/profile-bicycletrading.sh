# Copyright 2011, 2012 bicycle trading, llc

if [[ -n $BASH_VERSION ]]
then
  if [[ -f $HOME/.bashrc ]]
  then
    . $HOME/.bashrc
  fi
fi

if [[ -d $HOME/bin ]]
then
  PATH=$HOME/bin:$PATH
fi
