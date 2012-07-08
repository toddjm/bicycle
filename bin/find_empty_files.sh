#!/bin/bash
################################################################################
# Name: find_empty_files.sh
#
# Finds empty files and associated dates.
#
# Usage: find_empty_files.sh <asset class> <year>
# 
# Copyright 2011, 2012 bicycle trading, llc.
################################################################################

if [[ $# != 2 ]]
then
  echo "Usage: `basename $0` <asset class> <year>" 
  exit 1
fi

class=$1
year=$2

dir=~/bicycleticks/"$class"/ib

rm -f ~/tmp/*_empty*
rm -f $dir/*_empty*
cd $dir

case $class in
  futures)
    for i in `ls -1 | sed 's/\///'`
    do
      find $i -empty | awk "BEGIN {FS=\"/\"} \$4 == \"$year\" \\
        {print \$2, \$3, \$4\$5\$6}" > ~/tmp/"$class"_"$i"_"$year"_empty.txt
    done
  ;;
  equities | fx)
    for i in `ls -1 | sed 's/\///'`
    do
      find $i -empty | awk "BEGIN {FS=\"/\"} \$3 == \"$year\" \\
        {print \$2, \$3\$4\$5}" > ~/tmp/"$class"_"$i"_"$year"_empty.txt
    done
  ;;
esac
