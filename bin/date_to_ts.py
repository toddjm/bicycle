#!/usr/bin/python
"""
Convert UTC timestamp strings from mysqldump to
UNIX timestamps and reorganize output for tick files to be:

TIMESTAMP OPEN HIGH LOW CLOSE VOLUME COUNT VWAP GAPS

where TIMESTAMP, OPEN, HIGH, LOW, CLOSE, and VWAP are
type float and VOLUME, GAPS, and COUNT are type int.

"""

import calendar
import sys
import time

__author__ = "Todd Minehardt"
__copyright__ = "Copyright 2011, 2012 bicycle trading, llc"
__email__ = "todd@bicycletrading.com"


def date_to_ts(date):
    """
    Return UNIX timestamp from UTC timestamp string as
    returned from a mysqldump.

    """
    t_struct = time.strptime(date, '%Y-%m-%d %H:%M:%S')
    t_int = calendar.timegm(t_struct)
    return float(t_int)


def main():
    """Read old-type files and write new-type to stdout."""
    with open(sys.argv[1], 'r') as infile:
        for line in infile:
            t_stamp = date_to_ts(line.split()[0] + ' ' + line.split()[1])
            open_price = float(line.split()[2])
            high_price = float(line.split()[3])
            low_price = float(line.split()[4])
            close_price = float(line.split()[5])
            volume = line.split()[6]
            vwap = float(line.split()[7])
            gaps = line.split()[8]
            count = line.split()[9]
            print('{0:0f} {1:0f} {2:0f} {3:0f} {4:0f} '
                  '{5} {6} {7:0f} {8}').format(
                  t_stamp,
                  open_price,
                  high_price,
                  low_price,
                  close_price,
                  volume,
                  count,
                  vwap,
                  gaps)


if __name__ == '__main__':
    main()
