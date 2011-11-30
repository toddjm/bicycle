#!/bin/bash
# Copyright 2011 bicycle trading, llc.

# merge files with .tks and .tks_1 extensions

srcdir=/tmp/futures

if [[ ! -d $srcdir ]]
then
  echo "$srcdir not found."
  exit
fi

cd $srcdir

for file in `ls *_tks_1.txt`
do
  if [[ -s $file ]] && [[ -s ${file::- 6}.txt ]]
  then
    symbol=${file:: -16}
    expiry=${file: -16: -10}
    cat $file ${file:: -6}.txt > $symbol$expiry.all.txt
    date_to_ts.py $symbol$expiry.all.txt | sort -nk1 | uniq > $symbol$expiry.all.ts
    rename -f 's/\.all\.ts/\.tks/' $symbol$expiry.all.ts
  fi
done
