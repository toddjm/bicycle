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
    holidays_list_path = os.path.join(os.getenv('BICYCLE_HOME'),
                                      'share/dates')
    # Read holidays list from file.
    holidays = read_file(holidays_list_path, 'holidays.list')
    # Compare date to holidays, return True or False.
    if date.strftime('%Y-%m-%d') in holidays:
        return True
    else:
        return False


def read_file(path, name):
    """Return list of strings without newlines."""
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
    """Write ticks to files."""
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
                # Set timestamp from infile in UTC.
                timestamp = datetime.datetime.utcfromtimestamp(
                    float(infile[i].split()[0]))
                # Write data to outfile if timestamp and date match.
                if timestamp.strftime('%Y-%m-%d') == date.strftime('%Y-%m-%d'):
                    # Append newline to each line.
                    outfile.write(infile[i] + '\n')
            outfile.close()
    return


def main():
    """
    Creates ticker plant directories and populates
    appropriate directories therein.

    """
    months = [i for i in range(1, 13)]
    year = 2010

    # Set local_symbols_list_path.
    local_symbols_list_path = os.path.join(os.getenv('BICYCLE_HOME'),
                                           'etc/conf.d/asset-classes',
                                           'fx/data-sources/ib',
                                           'local-exchanges/idealpro')
    # Read local_symbols_list from file.
    local_symbols_list = read_file(local_symbols_list_path, 'symbols.txt')

    # Loop over symbols in local_symbols_list.
    for local_symbol in local_symbols_list:
        # Set path for writing tick files.
        tks_outfile_path = os.path.join(os.getenv('TICKS_HOME'),
                                        'fx',
                                        'ib',
                                        'idealpro',
                                        local_symbol)
        # Read ticks from file.
        tks_infile = read_file('/tmp/fx', local_symbol + '.tks')
        for month in months:
            # Write tick data to files.
            write_tks(year,
                      month,
                      local_symbol,
                      tks_infile,
                      tks_outfile_path)

if __name__ == '__main__':
    main()
