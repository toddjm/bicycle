#!/usr/bin/env python
"""
Read tick files and insert them on a by-day basis into
the appropriate directory.

"""

import calendar
import datetime
import os
import sys

__author__ = "Todd Minehardt"
__copyright__ = "Copyright 2011, bicycle trading, llc"
__email__ = "todd@bicycletrading.com"


def isholiday(date):
    """Returns True if date in holidays file, False otherwise."""
    # Set holidays_list_path.
    path = os.path.join(os.getenv('BICYCLE_HOME'), 'share/dates')
    # Read holidays list from file.
    holidays = read_file(path, 'holidays.list')
    # Compare date to holidays, return True or False.
    if date.strftime('%Y-%m-%d') in holidays:
        return True
    else:
        return False


def read_file(path, name):
    """Read from file and return a list of strings without newlines."""
    if not os.path.isdir(path):
        print("Directory {0} does not exist.".format(path))
        sys.exit()
    try:
        infile = open(os.path.join(path, name), 'r')
    except IOError:
        print("File {0} does not exist.".format(infile))
        sys.exit()
    values = infile.readlines()
    values = [line.strip() for line in values]
    infile.close()
    return values


def write_tks(year,
              month,
              symbol,
              infile,
              path):
    """Write ticks to files with .tks suffix."""
    # Number of days in month of designated year.
    days = calendar.monthrange(year, month)[1]
    for day in range(1, days + 1):
        # Set date in UTC.
        date = datetime.date(year, month, day)
        # Ensure that date is not a Saturday, Sunday, or holiday.
        if (date.weekday() < 5) and not isholiday(date):
            # Set directory for writing ticks.
            outdir = os.path.join(path,
                                  '{0:04d}'.format(year),
                                  '{0:02d}'.format(month),
                                  '{0:02d}'.format(day))
            # If outfile directory does not exist, create it and parents.
            if not os.path.isdir(outdir):
                os.makedirs(outdir, 0755)
            # Open outfile in append mode.
            try:
                outfile = open(os.path.join(outdir, symbol + '.tks'), 'a')
            except IOError:
                print("File {0} cannot be created.".format(outfile))
                sys.exit()
            # Iterate through infile.
            for i in range(len(infile)):
                # Set timestamp in UTC from field 0 of infile.
                timestamp = datetime.datetime.utcfromtimestamp(
                    float(infile[i].split()[0]))
                # Write to outfile if year, month, and day match.
                if timestamp.strftime('%Y-%m-%d') == date.strftime('%Y-%m-%d'):
                    # Append newline to each line before writing to file.
                    outfile.write(infile[i] + '\n')
            outfile.close()
    return


def main():
    """
    Creates ticker plant directories and populates
    appropriate directories therein.

    """
    # Set month numbers and year.
    months = [i for i in range(9, 12)]
    year = 2011

    # Set path for symbols list.
    path = os.path.join(os.getenv('BICYCLE_HOME'),
                        'etc/conf.d/asset-classes',
                        'fx/data-sources/ib',
                        'local-exchanges/idealpro')

    # Read symbols list from file.
    symbols = read_file(path, 'symbols.txt')

    # Loop over symbols.
    for symbol in symbols:
        # Set path for writing tick files.
        path = os.path.join(os.getenv('TICKS_HOME'),
                            'fx',
                            'ib',
                            'idealpro',
                            symbol)
        # Read ticks from file.
        infile = read_file('/tmp/fx', symbol + '.tks')
        for month in months:
            # Write tick data to files.
            write_tks(year,
                      month,
                      symbol,
                      infile,
                      path)

if __name__ == '__main__':
    main()
