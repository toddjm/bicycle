#!/bin/bash

outdir="$HOME/tmp"
symbols="AAPL AMZN GOOG"
srcdir="$TICKS_HOME/equities/ib/smart"
years="2010 2011 2012"

for i in $symbols
do
  outfile="$outdir/$i.close"
  rm -f $outfile
  for j in $years
  do
    for k in $(find $srcdir/$i/$j -type f -name "*.tks")
    do
      tail -1 $k | awk '{print $0}' | sort >> $outfile
    done
  done
done
