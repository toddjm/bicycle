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

#mysqldump \
#--no-create-info \
#--tab=$outdir \
#--tz-utc \
#--force \
#--ignore-table="$asset_class"_15sec.collect \
#--ignore-table="$asset_class"_15sec.collect_IB_errors \
#"$asset_class"_15sec

mysqldump \
--no-create-info \
--tab=$outdir \
--tz-utc \
--force \
--ignore-table="$asset_class"_15sec.collect \
--ignore-table="$asset_class"_15sec.collect_IB_errors \
--where="date(ts) >= '2012-03-29' and date(ts) <= '2012-04-02'" \
"$asset_class"_15sec

cd $outdir

for file in `ls *_tks.txt`
do
  date_to_ts.py $file | sort -nk1 | uniq > $file.ts
  rename -f 's/\_tks\.txt\.ts/\.tks/' $file.ts
done
