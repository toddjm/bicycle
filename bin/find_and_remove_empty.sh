#!/bin/bash
# Copyright 2011 bicycle trading, llc.

# this will locate files that are 14 Mb in size and print to stdout
#find . -type f -size 14c -printf "%s: %h%f\n"

# this will remove files that are 14 Mb in size
#find . -type f -size 14c -execdir rm -f {} \;

# this will find broken symlinks and print to stdout
#find -L . -type l -printf "%s: %h%f\n"

# this will find broken symlinks and remove them
#find -L . -type l -delete
