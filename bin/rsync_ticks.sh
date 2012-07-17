#!/bin/bash
#####################################################################
#
# rsync script, run as bicycle
#
# usage:
# rsync_ticks.sh [<asset class> <asset class> <asset class>]
#
# Copyright 2011, 2012 bicycle trading, llc
#
#####################################################################

if [[ $# > 3 ]]
then
  echo "Usage: `basename $0` [<asset class> <asset class> <asset class>]"
  exit 1
fi

if [[ $# == 0 ]]
then
  classes="fx"
else
  for i in $@
  do
    case $i in
      equities | futures | fx)
        classes="$classes $i"
      ;;
      *)
        echo "$i not found. Exiting."
        exit 1
      ;;
    esac
  done
fi

dir=$TICKS_HOME
hosts="x0 x1 x2 x3 y0 y1 y2"
options="-aPuvz --delete --ignore-existing"

for i in $classes
do
  for j in $hosts
  do 
    rsync $options $dir/$i bicycle@$j:$dir
  done
done

echo $?
