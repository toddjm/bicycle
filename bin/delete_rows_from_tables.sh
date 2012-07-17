#!/bin/bash
################################################################################
# Name: delete_rows_from_tables.sh
#
# Deletes rows from mysql tables.
#
# Usage: delete_rows_from_tables.sh <asset class> <start date> <end date>
# 
# Copyright 2011, 2012 bicycle trading, llc.
################################################################################

asset_class=$1
start_date=$2
end_date=$3

if [[ $# != 3 ]]
then
  echo "Usage: `basename $0` <asset class> <start date> <end date>"
  exit 1
fi

case $asset_class in
  equities | futures | fx)
  for i in 1day 15min 1min 15sec
  do 
    mysql -e "show tables in "$asset_class"_"$i";" |
    grep _tks > ~/tmp/"$asset_class"_"$i".tables
  done
  ;;
  *)
  echo "$asset_class does not exist."
  exit 1
  ;;
esac


#select * from equities_15min.SPY_tks where date(ts) > '2009-11-01' and date(ts) < '2010-01-01';
case $asset_class in
  equities | futures | fx)
  for i in 1day 15min 1min 15sec
  do
    for j in `cat ~/tmp/"$asset_class"_"$i".tables`
    do 
      mysql -e "delete from "$asset_class"_"$i"."$j" where \\
      date(ts) >= '$start_date' and date(ts) <= '$end_date';"
    done
  done
  ;;
  *)
  echo "$asset_class does not exist."
  exit 1
  ;;
esac
