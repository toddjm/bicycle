#!/bin/bash
# Copyright 2011 bicycle trading, llc.

if [[ $# != 2 ]]
then
    echo "Usage: $0 start_date end_date"
    exit
fi

IFS=$'\n'
srcdir=/tmp/futures/
current_date=`date +"%Y%m%d" -d "$1"`
end_date=`date +"%Y%m%d" -d "$2"`

# make sure we are in the futures directory
if [[ `basename $PWD` != futures ]]
then
    echo "Not in correct directory. Exiting..."
    exit
fi

# make sure the source directory exists
if [[ ! -d $srcdir ]]
then
    echo "$srcdir not found. Exiting..."
    exit
fi

symbols_exchanges_list="$BICYCLE_HOME/etc/conf.d/asset-classes/futures/data-sources/ib/symbols_exchanges.txt"

if [[ ! -e $symbols_exchanges_list ]]
then
  echo "$symbols_exchanges_list not found"
  exit
fi

holidays_list_path="$BICYCLE_HOME/share/dates"

if [[ ! -d $holidays_list_path ]]
then
    echo "$holidays_list_path not found"
    exit
fi

holidays_list="$holidays_list_path/holidays.txt"

if [[ ! -e $holidays_list ]]
then
    echo "$holidays_list not found"
    exit
fi

# list futures symbols and expiries.
for line in `cat $symbols_exchanges_list`
do
  symbol=`echo $line | cut -d ' ' -f1`
  exchange=`echo $line | cut -d ' ' -f2`
  while [[ $current_date != $end_date ]]
  do
    day_of_week=`date -d "$current_date" +%A`
    if [[ $day_of_week != Saturday ]] && \
      [[ $day_of_week != Sunday ]] && \
      [[ ! `grep $current_date $holidays_list` ]]
    then
      year=${current_date:0:4}
      month=${current_date:4:2}
      day=${current_date:6:2}
      dir_string="./$exchange/$symbol/$year/$month/$day/"
      if [[ ! -d $dir_string ]]
      then
        echo "creating $dir_string..." && mkdir -p $dir_string
      else
        echo "$dir_string exists, skipping..."
      fi
    fi
  current_date=`date +"%Y%m%d" -d "$current_date + 1 day"`
  done
done 
