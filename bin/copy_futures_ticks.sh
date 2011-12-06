#!/bin/bash
################################################################################
# Name: copy_futures_ticks.sh
#
# Copies .tks files from one location to another.
#
# Usage: copy_futures_ticks.sh <symbol> <year> <month>
#
# Copyright 2011 bicycle trading, llc.
################################################################################

symbol=$1
year=$2  # YYYY format
month=$3  # MM format
srcdir=/tmp/futures/  # directory with .tks files

if [[ ! $# == 3 ]]
then
  echo "Usage: $0 symbol year month"
  exit 1
fi

if [[ ! -d $srcdir ]]
then
  echo "$srcdir not found. Exiting..."
  exit
fi

# ensure we are in directory corresponding to symbol
if [[ `basename $PWD` != $symbol ]]
then
  echo "Not in correct directory. Exiting..."
  exit 1
fi

file="$srcdir$symbol$year$month.tks"
destination="./$year/$month"

if [[ ! -d $destination ]]
then
  echo "$destination not found. Exiting..."
  exit 1
fi

echo "File is: $file" && echo "Destination is: $destination"

cp $file $destination
