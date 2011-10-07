#!/bin/bash
# Copyright 2011 bicycle trading, llc.

asset_class=$1
symbol=$2

if [[ $# != 2 ]]
then
    echo "Usage: $0 asset_class symbol"
    exit
fi

if [[ $asset_class != "futures" ]] && \
   [[ $asset_class != "equities" ]] && \
   [[ $asset_class != "fx" ]]
then
    echo "$asset_class does not exist"
    exit
fi

for i in 1day 15min 1min 15sec
    do mysql -e "drop table if exists "$asset_class"_"$i"."$symbol"_tks;"
done
