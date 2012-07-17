#!/bin/bash
############################################
#
# rsync script, run as bicycle
#
# Copyright 2011, 2012 bicycle trading, llc
#
############################################

classes="equities futures fx"
dir="$TICKS_HOME"
hosts="x0 x1 x2 x3 y0 y1 y2"
options="-adlPruvz --ignore-existing"

for i in $classes
do
  for j in $hosts
  do 
    rsync $options $dir/$i bicycle@$j:$dir
  done
done
