#!/bin/bash

srcdir=~/tmp/futures

if [[ ! -d $srcdir ]]
then
  echo "$srcdir not found."
  exit
fi

cd $srcdir
rm -f *.expiry

for i in `find -O3 . \! -empty -name "*.tks"`
do
  file=${i:: -10}.expiry
  echo ${i: -10: -4} >> $file
done
