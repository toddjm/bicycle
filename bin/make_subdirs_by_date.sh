#!/bin/bash
# Copyright 2011 bicycle trading, llc.

exchange=$1
symbol=$2
srcdir=/tmp/futures/
months="01 02 03 04 05 06 07 08 09 10 11 12"
years="2009 2010 2011 2012 2013 2014 2015 2016 2017 2018 2019 2020 2021 2022"

# correct usage
if [[ ! $# == 2 ]]
then
  echo "Usage: `basename $0` exchange symbol"
  exit 1
fi

# make sure we are in an exchange directory
if [[ `basename $PWD` != $exchange ]]
then
  echo "Not in correct directory. Exiting."
  exit 2
fi

# make sure the source directory exists
if [[ ! -d $srcdir ]]
then
  echo "$srcdir not found. Exiting."
  exit 3
fi

# make directories if needed
for i in $years
do
  if [[ $i == 2009 ]]
  then
    for j in 09 10 11 12
    do
      destination="./$symbol/$i/$j"
      if [[ ! -d $destination ]]
      then
        echo "Creating $destination"
        mkdir -p $destination
       fi
    done
  else
    for j in $months
    do
      destination="./$symbol/$i/$j"
      if [[ ! -d $destination ]]
      then
        echo "Creating $destination"
        mkdir -p $destination
      fi
    done
  fi
done

# copy files to destination directories
#for i in $years
#do
#    for j in $months
#    do
#        destination="./$symbol/$i/$j"
#        file="$srcdir$symbol$i$j.tks"
#        if [[ -f $file && -d $destination ]]
#        then
#            echo "Copying $file to $destination"
#            cp $file $destination
#        fi
#    done
#done
