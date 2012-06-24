#!/bin/bash
################################################################################
# Name: db_to_flat_file.sh
#
# Creates sorted uniquely-indexed flat .tks files from mysqldump.
#
# Usage: db_to_flat_file.sh <asset class> <start date> [<end date>]
#
# Copyright 2011, 2012 bicycle trading, llc.
################################################################################

if [[ $# < 2 || $# > 3 ]]
then
  echo "Usage: `basename $0` asset-class start-date [end-date]"
  exit 1
fi

class=$1
s_date=$2
if [[ $# = 3 ]]
then
  e_date=$3
else
  e_date=$(date +%Y-%m-%d)
fi

o_dir="$HOME/tmp/$class"

if [[ ! -d $o_dir ]]
then
  echo "$o_dir not found."
  exit 1
fi

cd $o_dir
rm -f $o_dir/*.*

mysqldump \
--no-create-info \
--tab=$o_dir \
--tz-utc \
--force \
--ignore-table="$class"_15sec.collect \
--ignore-table="$class"_15sec.collect_IB_errors \
--where="date(ts) >= '"$s_date"' and date(ts) <= '"$e_date"'" \
"$class"_15sec
#--where="date(ts) >= '2012-01-01' and date(ts) <= '2012-06-15'" \
#"$class"_15sec

list=$(find -O3 $o_dir \! -empty -name "*_tks.txt")
for i in $list
do
  file=${i%"_tks.txt"}.tks
  date_to_ts.py $i | sort -unk1 > $file
done

if [[ $class = futures ]]
then
  list=$(find -O3 $o_dir \! -empty -name "*.tks")
  for i in $list
    do
      length=${#i}
      end=$((length - 10))
      file=${i:0:$end}.expiry
      echo ${i:$end:6} >> $file
    done
fi
