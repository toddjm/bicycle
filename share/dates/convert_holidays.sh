#!/bin/bash

holidays_file=$1

if [[ ! -e $holidays_file ]]
then
    echo "$holidays_file not found."
    exit
fi

while read line
do
    echo "${line:0:4}-${line:4:2}-${line:6}"
done < $holidays_file
