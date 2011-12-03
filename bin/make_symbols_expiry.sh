#!/bin/bash

srcdir=/tmp/futures

if [[ ! -d $srcdir ]]
then
  echo "$srcdir not found."
  exit
fi

cd $srcdir

for i in `ls *.tks`
do
  file="${i:: -10}.expiry"
  echo ${i: -10: -4} >> $file
done
     
