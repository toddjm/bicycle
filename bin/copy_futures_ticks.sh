#!/bin/bash
# Copyright 2011 bicycle trading, llc.

symbol=$1
year=$2
month=$3
srcdir=/tmp/futures/

if [[ ! $# == 3 ]]
then
    echo "Usage: $0 symbol year month"
    exit
fi

if [[ `basename $PWD` != $symbol ]]
then
    echo "Not in correct directory. Exiting..."
    exit
fi

if [[ ! -d $srcdir ]]
then
    echo "$srcdir not found. Exiting..."
    exit
fi

file="$srcdir$symbol$year$month.tks"
destination="./$year/$month"

if [[ ! -d $destination ]]
then
    echo "$destination not found. Exiting..."
    exit
fi

echo "File is: $file"
echo "Destination is: $destination"

cp $file $destination
