#!/usr/bin/env python
"""
Convert UTC timestamps to UNIX timestamps and reorganize
output for tick files to be:

UNIX_TIMESTAMP OPEN HIGH LOW CLOSE VOLUME COUNT VWAP GAPS

"""

import calendar
import sys
import time

__author__ = "Todd Minehardt"
__copyright__ = "Copyright 2011, bicycle trading, llc"
__maintainer__ = "Todd Minehardt"
__email__ = "todd@bicycletrading.com"


def date_to_ts(date_str):
    """Return UNIX timestamp from UTC timestamp."""
    return float(calendar.timegm(
        time.strptime(date_str, '%Y-%m-%d %H:%M:%S')))


def main():
    """Read old-type files and write new-type to stdout."""
    with open(sys.argv[1], 'r') as data:
        for line in data:
            timestamp = date_to_ts(line.split()[0] + ' ' + line.split()[1])
            open_price = line.split()[2]
            high_price = line.split()[3]
            low_price = line.split()[4]
            close_price = line.split()[5]
            volume = line.split()[6]
            vwap = line.split()[7]
            gaps = line.split()[8]
            count = line.split()[9]
            print '{0} {1} {2} {3} {4} {5} {6} {7} {8}'.format(
                timestamp,
                float(open_price),
                float(high_price),
                float(low_price),
                float(close_price),
                volume,
                count,
                float(vwap),
                gaps)

if __name__ == '__main__':
    main()
