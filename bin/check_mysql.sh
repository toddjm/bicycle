#!/bin/bash

class=$1
symbol=$2

case $class in
  futures)
  for i in `mysql --skip-column-names -e "select concat(id, contract) from unicycle.futures_roll_dates;"`
  do
    echo $i 
    mysql -N -s -e "select date(t1.ts) from unicycle."$class"_valid_1day \\
                    as t1 left join "$class"_1day."$i"_tks as t2 on \\
                    (date(t1.ts) = date(t2.ts)) where date(t2.ts) is null \\
                    and date(t1.ts) <= (select max(date(ts)) from \\
                    "$class"_1day."$i"_tks) and date(t1.ts) >= \\
                    date_sub(now(), interval 6 month);" 2> /dev/null
    echo
  done
#    do echo $i && mysql --skip-column-names -e "select date(t1.ts) \\
#     from unicycle."$class"_valid_1day as t1 left \\
#     join "$class"_1day."$i"_tks as t2 on \\
#     (date(t1.ts) = date(t2.ts)) where date(t2.ts) \\
#     is null and date(t1.ts) <= (select max(date(ts)) \\
#     from "$class"_1day."$i"_tks) and \\
#     date(t1.ts) >= (select min(date(ts)) \\
#     from "$class"_1day."$i"_tks);"
#    done
  ;;
  equities | fx)
  mysql --skip-column-names -e "select date(t1.ts) \\
    from unicycle."$class"_valid_1day as t1 left \\
    join "$class"_1day."$symbol"_tks as t2 on \\
    (date(t1.ts) = date(t2.ts)) where date(t2.ts) \\
    is null and date(t1.ts) <= (select max(date(ts)) \\
    from "$class"_1day."$symbol"_tks) and \\
    date(t1.ts) >= (select min(date(ts)) from \\
    "$class"_1day."$symbol"_tks);"
  ;;
  *)
  ;;
esac
