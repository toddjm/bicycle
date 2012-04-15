#!/bin/bash
################################################################################
# Name: find_empty_files.sh
#
# Finds empty files and associated dates.
#
# Usage: find_empty_files.sh <asset class>
# 
# Copyright 2011, 2012 bicycle trading, llc.
################################################################################

asset_class=$1

if [[ $# != 1 ]]
then
  echo "Usage: $0 <asset class>"
  exit 1
fi

dir=~/bicycleticks/"$asset_class"/ib

cd $dir

case $asset_class in
  futures)
    for i in `ls -1 | sed 's/\///'`
    do
      find $i -empty | awk 'FS="/" {print $2$3, $4$5$6}' > "$i"_empty.txt
    done
  ;;
  equities fx)
    for i in `ls -1 | sed 's/\///'`
    do
      find $i -empty | awk 'FS="/" {print $2, $3$4$5}' > "$i"_empty.txt
    done
  ;;
  *)
  ;;
esac
