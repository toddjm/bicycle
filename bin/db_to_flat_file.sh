#!/bin/bash
################################################################################
# Name: db_to_flat_file.sh
#
# Creates sorted flat .tks files from mysqldump.
#
# Usage: db_to_flat_file.sh <asset class>
#
# Copyright 2011, 2012 bicycle trading, llc.
################################################################################

asset_class=$1
outdir="$HOME/tmp/$asset_class"

if [[ $# != 1 ]]
then
  echo "Usage: $0 asset_class"
  exit 1
fi

if [[ ! -d $outdir ]]
then
  echo "$outdir not found. Exiting..."
  exit 1
fi

mysqldump \
--no-create-info \
--tab=$outdir \
--tz-utc \
--force \
--ignore-table="$asset_class"_15sec.collect \
--ignore-table="$asset_class"_15sec.collect_IB_errors \
--where="date(ts) >= '2012-01-01' and date(ts) < '2012-04-28'" \
"$asset_class"_15sec

cd $outdir

rm -f *.sql

find -O3 $outdir -empty -name "*_tks.txt" -exec rm -f '{}' \;

for i in `find -O3 $outdir \! -empty -name "*_tks.txt"`
do
  file=${i%"_tks.txt"}.tks
  date_to_ts.py $i | sort -unk1 > $file
done

if [[ $asset_class == futures ]]
then
  rm -f *.expiry
  for i in `find -O3 $outdir \! -empty -name "*.tks"`
    do
      length=${#i}
      end=$((length - 10))
      file=${i:0:$end}.expiry
      echo ${i:$end:6} >> $file
    done
fi

find -O3 $outdir -name "*_tks.txt" -exec rm -f '{}' \;
