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
  tables=$(mysql -N -s -e "select table_name from \\
                           information_schema.tables \\
                           where table_schema = '$db' \\
                           and table_rows > 1;")
  s_date=$(date +%s -d "now - 6 months")
  if [[ $# == 2 ]]
  then
    x="$2"_tks
    if [[ ! $tables =~ $x ]]
    then
      echo "Symbol not found."
      exit 1
    else
      tables=$x
    fi
  fi
  ;;
*)
  echo "Unknown asset class"
  exit 1
  ;;
esac

#for i in $tables
#do
#  if [[ $class = 'futures' ]]
#  then
#    t_date=$(date +%s -d "${i: -10: -4}01")
#    if (( t_date >= s_date ))
#    then
#      echo ${i::(-4)}
#      mysql -N -s -e "select date(t1.ts) from "$dates" \\
#                      as t1 left join "$db"."$i" \\
#                      as t2 on (date(t1.ts) = date(t2.ts)) \\
#                      where date(t2.ts) is null and \\
#                      date(t1.ts) <= (select max(date(ts)) \\
#                      from "$db"."$i") and \\
#                      date(t1.ts) >= date_sub(now(), \\
#                      interval 6 month);"
#      echo
#    fi
#  else
#    echo ${i::(-4)}
#    mysql -N -s -e "select date(t1.ts) from "$dates" \\
#                    as t1 left join "$db"."$i" \\
#                    as t2 on (date(t1.ts) = date(t2.ts)) \\
#                    where date(t2.ts) is null and \\
#                    date(t1.ts) <= (select max(date(ts)) \\
#                    from "$db"."$i") and \\
#                    date(t1.ts) >= date_sub(now(), \\
#                    interval 6 month);"
#    echo
#  fi
#done

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
