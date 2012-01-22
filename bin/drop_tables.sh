#!/bin/bash
################################################################################
# Name: drop_tables.sh
#
# Drops mysql tables for symbols.
#
# Usage: drop_tables.sh <asset class> <symbol>
# 
# Copyright 2011 bicycle trading, llc.
################################################################################

asset_class=$1
symbol=$2

if [[ $# != 2 ]]
then
  echo "Usage: $0 asset_class symbol"
  exit 1
fi

case $asset_class in
  equities | futures | fx)
  for i in 1day 15min 1min 15sec
    do mysql -e "drop table if exists "$asset_class"_"$i"."$symbol"_tks;"
    done
  ;;
  *)
    echo "$asset_class does not exist."
    exit 1
  ;;
esac
