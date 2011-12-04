#!/bin/bash
# Copyright 2011 bicycle trading, llc.

asset_class=$1
outdir="$HOME/tmp/$asset_class"

if [[ $# != 1 ]]
then
    echo "Usage: $0 asset_class"
    exit
fi

if [[ ! -d $outdir ]]
then
    echo "$outdir not found."
    exit
fi

mysqldump \
--no-create-info \
--tab=$outdir \
--tz-utc \
--force \
--ignore-table="$asset_class"_15sec.collect \
--ignore-table="$asset_class"_15sec.collect_IB_errors \
"$asset_class"_15sec

cd $outdir

for file in `ls *_tks.txt`
do
  date_to_ts.py $file | sort -nk1 | uniq > $file.ts
  rename -f 's/\_tks\.txt\.ts/\.tks/' $file.ts
done
