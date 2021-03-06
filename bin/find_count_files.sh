#!/bin/bash
################################################################################
# Name: find_count_files.sh
#
# Returns wc -l for non-empty files and their associated dates.
#
# Usage: find_count_files.sh <asset class> <year>
# 
# Copyright 2011, 2012 bicycle trading, llc.
################################################################################

asset_class=$1
year=$2

if [[ $# != 2 ]]
then
  echo "Usage: $0 <asset class> <year>" 
  exit 1
fi

dir=~/bicycleticks/"$asset_class"/ib

rm -f ~/tmp/*_count*
rm -f $dir/*_count*
cd $dir

case $asset_class in
  futures)
    for i in `ls -1 | sed 's/\///'`
    do
      find $i -empty | awk "BEGIN {FS=\"/\"} \$4 == \"$year\" \\
        {print \$2, \$3, \$4\$5\$6}" > ~/tmp/"$asset_class"_"$i"_"$year"_count.txt
    done
  ;;
  equities | fx)
    for i in `ls -1 | sed 's/\///'`
    do
      find $i -empty | awk "BEGIN {FS=\"/\"} \$3 == \"$year\" \\
        {print \$2, \$3\$4\$5}" > ~/tmp/"$asset_class"_"$i"_"$year"_count.txt
    done
  ;;
esac
