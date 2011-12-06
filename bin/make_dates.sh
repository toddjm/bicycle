#!/bin/bash
################################################################################
# Name: make_dates.sh
#
# Makes directories of the form <symbol>/YYYY/MM/DD.
#
# Usage: make_dates.sh <start date> <end date> <symbol>
#
# Copyright 2011 bicycle trading, llc.
################################################################################

if [[ $# != 3 ]]
then
  echo "Usage: $0 start_date end_date symbol"
  exit 1
fi

current_date=`date +"%Y%m%d" -d "$1"`
end_date=`date +"%Y%m%d" -d "$2"`
symbol=$3

if [[ ! -d "./$symbol" ]]
then
  echo "./$symbol not found. Exiting..."
  exit 1
fi

# set path for holidays list
holidays_list_path="$BICYCLE_HOME/share/dates"

if [[ ! -d $holidays_list_path ]]
then
  echo "$holidays_list_path not found. Exiting..."
  exit 1
fi

holidays_list="$holidays_list_path/holidays.txt"

if [[ ! -e $holidays_list ]]
then
  echo "$holidays_list not found. Exiting..."
  exit 1
fi

# loop over dates until (end date) - 1 day
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
    dir_string="./$symbol/$year/$month/$day/"
    if [[ ! -d $dir_string ]]
    then
      echo "creating $dir_string..." && mkdir -p $dir_string
    else
      echo "$dir_string exists, skipping..."
     fi
  fi
  current_date=`date +"%Y%m%d" -d "$current_date + 1 day"`
done
