#!/bin/bash
################################################################################
# Name: rolling_ticks.sh
#
# Output volume traded for dates for contracts.
#
# Usage: rolling_ticks.sh <symbol> <contract>
# 
# Copyright 2011, 2012 bicycle trading, llc.
################################################################################

if [[ $# != 4 ]]
then
  echo "Usage: `basename $0` <symbol> <current> <next> <exchange>" 
  exit 1
fi

symbol="CL"
current="201205"
next="201206"
exchange="nymex"

for i in $(find $TICKS_HOME/futures/ib/$exchange/$symbol/$current -type f -name "*.tks")
do
  year=${i:(-17):(-13)}
  month=${i:(-12):(-10)}
  day=${i:(-9):(-7)}
  echo -e $year-$month-$day $(awk '{sum += $6} END {print sum}' < $i)
done | sort -k1

