/******************************************************************************
* format.c: read files from mysqldump, write with proper time and numeric     *
*           format to file.                                                   *
*                                                                             *
* usage: format <infile>                                                      *
*                                                                             *
*        where                                                                *
*                                                                             *
*        the fields of infile are tab-separated, total of nine (9) with       *
*        field one (1) formatted as YYYY-MM-DD HH:MM:SS in UTC as 'ts';       *
*        fields two (2) through five (5) inclusive are floats corresponding   *
*        to 'open', 'high', 'low', and 'close,' respectively; field six (6)   *
*        an int for 'volume'; field seven (7) a float for 'vwap'; field       *
*        eight (8) an int (valued 0 or 1) for 'gaps'; and field nine (9)      *
*        an int for 'orders'.                                                 *
*                                                                             *
*        the fields of outfile are space-separated, total of nine (9) with    *
*        field one (1) formatted as a float for UTC Unix timestamp; fields    *
*        two (2) through five (5) inclusive formatted as floats for 'open',   *
*        'high', 'low', and 'close'; fields six (6) and seven (7) are ints    *
*        for 'volume' and 'orders'; field eight (8) is a float for 'vwap';    *
*        and field nine (9) is an int for 'gaps'.                             */

/* Libraries. */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

struct tick {
    int year,
        month,
        day,
        hour,
        minute,
        second,
        volume,
        orders,
        gaps;
    float open,
          high,
          low,
          close,
          vwap; 
};

typedef struct tick tick;

main(int argc, char *argv[])
{
 
FILE *fp;

fp = fopen(argv[1], "r");

tick a;

while (feof(fp) == 0) {
    fscanf(fp, "%d-%d-%d %d-%d-%d[^\t]%f[^\t]%f[^\t]%f[^\t]%f[^\t]%d[^\t]%f[^\t]%d[^\t]%d\n",
         &a.year,
         &a.month,
         &a.day,
         &a.hour,
         &a.minute,
         &a.second,
         &a.open,
         &a.high,
         &a.low,
         &a.close,
         &a.volume,
         &a.vwap,
         &a.gaps,
         &a.orders);
 
    printf("%d %d %d %d %d %d\n",
          a.year,
          a.month,
          a.day,
          a.hour,
          a.minute,
          a.second);
}

    fclose(fp);

return 0;
}
