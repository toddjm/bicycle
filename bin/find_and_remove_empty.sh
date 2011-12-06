#!/bin/bash
################################################################################
# Name: find_and_remove_empty.sh
#
# Finds and removes empty files and/or symlinks.
#
# Usage: find_and_remove_empty.sh <show|remove> <files|symlinks>
#
# Copyright 2011 bicycle trading, llc.
################################################################################

if [[ $# != 2 ]]
then
  echo "Usage: $0 show|remove files|symlinks"
  exit 1
fi

action=$1
target=$2

case $action in
  show)
    if [[ $target == "files" ]]
    then
      echo "Looking for files..."
      find . -type f -size 14c -printf "%s: %h%f\n"
    elif [[ $target == "symlinks" ]]
    then
      echo "Looking for symlinks..."
      find -L . -type l -printf "%s: %h%f\n"
    fi
    ;;
  remove)
    if [[ $target == "files" ]]
    then
      echo "Removing files..."
      find . -type f -size 14c -execdir rm -f {} \;
    elif [[ $target == "symlinks" ]]
    then
      echo "Removing symlinks..."
      find -L . -type l -delete
    fi
    ;;
  *)
    ;;
esac
    
# this will locate files that are 14 Mb in size and print to stdout
#find . -type f -size 14c -printf "%s: %h%f\n"

# this will remove files that are 14 Mb in size
#find . -type f -size 14c -execdir rm -f {} \;

# this will find broken symlinks and print to stdout
#find -L . -type l -printf "%s: %h%f\n"

# this will find broken symlinks and remove them
#find -L . -type l -delete
