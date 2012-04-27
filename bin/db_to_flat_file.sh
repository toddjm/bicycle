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

#mysqldump \
#--no-create-info \
#--tab=$outdir \
#--tz-utc \
#--force \
#--ignore-table="$asset_class"_15sec.collect \
#--ignore-table="$asset_class"_15sec.collect_IB_errors \
#--where="date(ts) >= '2011-02-01' and date(ts) <= '2012-04-09'" \
#"$asset_class"_15sec NG201201_tks NG201202_tks NG201203_tks NG201204_tks \
#NG201205_tks NG201206_tks NG201207_tks NG201208_tks NG201209_tks NG201210_tks \
#NG201211_tks NG201212_tks NG201105_tks NG201106_tks NG201107_tks NG201108_tks \
#NG201109_tks NG201110_tks NG201111_tks NG201112_tks

mysqldump \
--no-create-info \
--tab=$outdir \
--tz-utc \
--force \
--ignore-table="$asset_class"_15sec.collect \
--ignore-table="$asset_class"_15sec.collect_IB_errors \
--where="date(ts) >= '2012-04-01' and date(ts) <= '2012-04-05'" \
"$asset_class"_15sec CL201206_tks ZB201209_tks WTI201212_tks

cd $outdir

case $asset_class in
  equities | futures)
    for i in `ls *_tks.txt`
    do
      n=${i%"_tks.txt"}
      awk -F"\t" 'system("date -ud \""$1"\" +%s")' $i > t
      awk -F"\t" '{printf "%f %f %f %f %d %d %f %d\n", $2, $3, $4, $5, $6, $9, $7, $8}' $i > d
      paste -d" " t d > f
      sort -unk1 f > $n.tks
      rm -f t d f
    done
    ;;
  fx)
    for i in `ls *_tks.txt`
    do
      n=${i%"_tks.txt"}
      awk -F"\t" 'system("date -ud \""$1"\" +%s")' $i > t
      awk -F"\t" '{printf "%f %f %f %f %d %d %d %d\n", $2, $3, $4, $5, $6, $9, $7, $8}' $i > d
      paste -d" " t d > f
      sort -unk1 f > $n.tks
      rm -f t d f
    done
    ;;
esac
