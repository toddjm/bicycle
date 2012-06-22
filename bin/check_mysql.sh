#!/bin/bash

if [[ $# != 1 ]]
then
  echo "Usage: `basename $0` <asset class>"
  exit 1
fi

case $1 in
equities | futures | fx)
  asset_class=$1
  dates=unicycle."$asset_class"_valid_1day
  db="$asset_class"_1day
  symbols=unicycle."$asset_class"_symbols
  ;;
*)
  echo "Unknown asset class"
  exit 1
  ;;
esac

for i in `mysql -N -s -e "select * from "$symbols";"` 
do
  echo $i 
  mysql -N -s -e "select date(t1.ts) from "$dates" \\
                  as t1 left join "$db"."$i"_tks as t2 on \\
                  (date(t1.ts) = date(t2.ts)) where date(t2.ts) is null \\
                  and date(t1.ts) <= (select max(date(ts)) from \\
                  "$db"."$i"_tks) and date(t1.ts) >= \\
                  date_sub(now(), interval 6 month);" 2> /dev/null
  echo
done
