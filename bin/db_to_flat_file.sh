#!/bin/bash
# Copyright 2011 bicycle trading, llc.

asset_class=$1
outdir="/tmp/$asset_class"

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

for i in `ls *_tks.txt`; do sort -nk1 $i > $i.sorted; done

for i in `ls *_tks.txt.sorted`; do rename 's/\_tks\.txt\.sorted/\.tks/' $i; done

for i in `ls *.tks`; do date_to_ts.py $i > $i.ts; done

for i in `ls *.tks`; do rename -f 's/\.tks/\.tks\.orig/' $i; done

for i in `ls *.tks.ts`; do rename -f 's/\.tks\.ts/\.tks/' $i; done
