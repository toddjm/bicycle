#!/bin/bash
################################################################################
# Name: db_to_flat_file_by_symbol.sh
#
# Creates sorted uniquely-indexed flat .tks files from mysqldump.
#
# Usage: db_to_flat_file.sh <asset class> <start date> [<end date>]
#
# Copyright 2011, 2012 bicycle trading, llc.
################################################################################

if [[ $# < 3 || $# > 4 ]]
then
  echo "Usage: `basename $0` <asset class> <symbol> <start date> [end date]"
  exit 1
fi

class=$1
symbol=$2
begin=$3

if [[ $# = 4 ]]
then
  end=$4
else
  end=$(date +%Y-%m-%d)
fi

outdir="$HOME/tmp/$class"

if [[ ! -d $outdir ]]
then
  echo "$outdir not found."
  exit 1
fi

cd $outdir
rm -f $outdir/"$symbol".*

mysqldump \
--no-create-info \
--tab=$outdir \
--tz-utc \
--force \
--ignore-table="$class"_15sec.collect \
--ignore-table="$class"_15sec.collect_IB_errors \
--where="date(ts) >= '"$begin"' and date(ts) <= '"$end"'" \
"$class"_15sec "$symbol"_tks


list=$(find -O3 $outdir \! -empty -name "*_tks.txt")
for i in $list
do
  file=${i%"_tks.txt"}.tks
  date_to_ts.py $i | sort -unk1 > $file
done

if [[ $class = futures ]]
then
  list=$(find -O3 $outdir \! -empty -name "*.tks")
  for i in $list
  do
    length=${#i}
    end=$((length - 10))
    expiry_file=${i:0:$end}.expiry
    echo ${i:$end:6} >> $expiry_file
  done
fi
