#!/bin/bash

if [[ $# < 1 || $# > 4 ]]
then
  echo "Usage: `basename $0` <asset class> [symbol] [start] [end]"
  exit 1
fi

case $1 in
equities | futures | fx)
  class=$1
  dates=unicycle."$class"_valid_1day
  db="$class"_1day
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
2 | 3 | 4)
  tables=$(mysql -N -s -e "select table_name from \\
                           information_schema.tables \\
                           where table_schema = '$db' \\
                           and table_name like '$2%_tks' \\
                           and table_rows > 1;")
  ;;
esac

case $# in
1 | 2)
  start_date=$(date +%s -d "now - 6 months")
  end_date=$(date +%s -d "now")
  ;;
3)
  start_date=$(date +%s -d "$3")
  end_date=$(date +%s -d "now")
  ;;
4)
  start_date=$(date +%s -d "$3")
  end_date=$(date +%s -d "$4")
  if (( end_date > $(date +%s -d "now") ))
  then
    end_date=$(date +%s -d "now")
  fi
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
    length=${#i}
    symbol_length=$((length - 10))
    contract=${i:$symbol_length:6}
    contract_date=$(date +%s -d "${contract}01")
    if (( contract_date >= start_date ))
    then
      echo ${i:0:$symbol_length}$contract
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
