#!/bin/bash
# Copyright 2011 bicycle trading, llc.

IFS=$'\n'
rootdir=$BICYCLE_HOME/etc/conf.d/futures/ib

# make sure we are in the correct directory
if [[ `echo $PWD` != $rootdir ]]
then
  echo "Not in correct directory. Changing..."
  cd $rootdir
fi

exchanges_list="$rootdir/exchanges.txt"
if [[ ! -e $exchanges_list ]]
then
  echo "$exchanges_list not found"
  exit
fi

symbols_exchanges_list="$rootdir/symbols_exchanges.txt"
if [[ ! -e $symbols_exchanges_list ]]
then
  echo "$symbols_exchanges_list not found"
  exit
fi

# make sure exchanges dir exists; if not, create it.
exchangedir="$rootdir/exchanges"
if [[ ! -d $exchangedir ]]
then
  echo "Creating $exchangedir..."
  mkdir $exchangedir
fi

# change to proper directory.
cd $exchangedir

# make exchange directories.
for exchange in `cat $exchanges_list`
do
  if [[ ! -d $exchange ]]
  then
    echo "Creating $exchange..." && mkdir $exchange
  fi
done

# create symbols.txt files in each dir, append with symbols.
for exchange in `cat $exchanges_list`
do
  for symbol in `grep -w $exchange $symbols_exchanges_list | cut -d ' ' -f1`
  do
    echo $symbol >> $exchange/symbols.txt
  done
done
