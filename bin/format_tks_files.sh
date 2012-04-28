#!/bin/bash
################################################################################
# Name: format_tks_files.sh
#
# Save backup and reformat tks files correctly.
#
# Usage: format_tks_files.sh <asset class> <year>
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
  equities)
  cd smart
  for i in `ls -1`
  do 
    for j in `find $i ! -empty -name "*.tks" -print`
    do 
      awk "{ printf \"%f %f %f %f %f %d %d %f %d\n\", \$1, \$2, \$3, \\
        \$4, \$5, \$6, \$7, \$8, \$9 }" $j > $j.fix \\
        && sort -nk1 $j.fix > $j.fix.1 && sort -unk1 $j.fix.1 > $j.fix.2 \\
        && rename -f 's/\.fix\.2//' $j.fix.2 && rm -f $j*.fix $j*.fix.1
    done
  done
  ;;
  futures)
    for i in `find . ! -empty -name "*.tks" -print`
    do
      awk "{printf \"%f %f %f %f %f %d %d %f %d\n\", \$1, \$2, \$3, \\
        \$4, \$5, \$6, \$7, \$8, \$9}" $i > "$i.fix" && mv "$i.fix" $i
    done
  ;;
  fx)
    for i in `find . ! -empty -name "*.tks" -print`
    do
      awk "{printf \"%f %f %f %f %f %d %d %d %d\n\", \$1, \$2, \$3, \\
        \$4, \$5, \$6, \$7, \$8, \$9}" $i > "$i.fix" && mv "$i.fix" $i
    done
  ;;
esac
