#!/bin/bash

if [[ $# < 1 || $# > 2 ]]
then
  echo "Usage: `basename $0` <asset class> [symbol]"
  exit 1
fi

case $1 in
equities | futures | fx)
  class=$1
  dates=unicycle."$class"_valid_1day
  db="$class"_1day
  s_date=$(date +%s -d "now - 6 months")
#  d_date="2012-01-01"
  ;;
*)
  echo "Unknown asset class"
  exit 1
  ;;
esac

case $# in
1)
  tables=$(mysql -N -s -e "select table_name from \\
                           information_schema.tables \\
                           where table_schema = '$db' \\
                           and table_rows > 1;")
  ;;
2)
  tables=$(mysql -N -s -e "select table_name from \\
                           information_schema.tables \\
                           where table_schema = '$db' \\
                           and table_name like '$2%_tks' \\
                           and table_rows > 1;")
  ;;
esac

if [[ ${#tables} = 0 ]]
then
  echo "Symbol not found."
  exit 1
fi

if [[ $class = 'futures' ]]
then
  for i in $tables
  do
    t_date=$(date +%s -d "${i:(-10):(-4)}01")
    if (( t_date >= s_date ))
    then
      echo ${i::(-4)}
      mysql -N -s -e "select date(t1.ts) from "$dates" \\
                      as t1 left join "$db"."$i" \\
                      as t2 on (date(t1.ts) = date(t2.ts)) \\
                      where date(t2.ts) is null and \\
                      date(t1.ts) <= (select max(date(ts)) \\
                      from "$db"."$i") and \\
                      date(t1.ts) >= date_sub(now(), \\
                      interval 6 month);"
#      mysql -N -s -e "select date(t1.ts) from "$dates" \\
#                      as t1 left join "$db"."$i" \\
#                      as t2 on (date(t1.ts) = date(t2.ts)) \\
#                      where date(t2.ts) is null and \\
#                      date(t1.ts) <= (select max(date(ts)) \\
#                      from "$db"."$i") and date(t1.ts) >= '$d_date';"
      echo
    fi
  done
else
  for i in $tables
  do
    echo ${i::(-4)}
    mysql -N -s -e "select date(t1.ts) from "$dates" \\
                    as t1 left join "$db"."$i" \\
                    as t2 on (date(t1.ts) = date(t2.ts)) \\
                    where date(t2.ts) is null and \\
                    date(t1.ts) <= (select max(date(ts)) \\
                    from "$db"."$i") and \\
                    date(t1.ts) >= date_sub(now(), \\
                    interval 6 month);"
    echo
  done
fi

exit 0
