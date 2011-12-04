#!/usr/bin/env python
"""
Read tick files and insert them on a by-day basis into
the appropriate directory.

"""

import argparse
import configobj
import datetime
import os
import sys

__author__ = "Todd Minehardt"
__copyright__ = "Copyright 2011, bicycle trading, llc"
__email__ = "todd@bicycletrading.com"


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


# Read holidays list from file.
HOLIDAYS = []
HOLIDAYS = read_file(os.path.join(
                                  os.getenv('BICYCLE_HOME'),
                                  'share/dates'),
                                  'holidays.list')


def check_date(date):
    """
    Returns True if date is not a Saturday or Sunday or
    holiday, False otherwise.
    """
    # Ensure that date is not a Saturday, Sunday, or holiday.
    if (date.weekday() < 5) and (date.strftime('%Y-%m-%d') not in HOLIDAYS):
        return True
    else:
        return False


def write_ticks(start,
                end,
                symbol,
                data,
                path):
    """Write ticks to files with .tks suffix."""
    # Adjust start and end based on data start/end.
    first = datetime.datetime.utcfromtimestamp(float(data[0].split()[0]))
    last = datetime.datetime.utcfromtimestamp(float(data[-1].split()[0]))
    if first > start:
        date = first
    else:
        date = start
    if last < end:
        end = last
    while date <= end:
        # Make sure date is not on a weekend or holiday.
        if check_date(date):
            # Set directory for writing ticks.
            outdir = os.path.join(path,
                                  '{0:04d}'.format(date.year),
                                  '{0:02d}'.format(date.month),
                                  '{0:02d}'.format(date.day))
            # If directory does not exist, create it and parents.
            if not os.path.isdir(outdir):
                os.makedirs(outdir, 0755)
            # Set name of output .tks file.
            tksfile = os.path.join(outdir, symbol + '.tks')
            # Create outfile in append mode.
            try:
                outfile = open(tksfile, 'a')
            except IOError:
                print("File {0} cannot be created.".format(outfile))
                sys.exit()
            # Iterate through data.
            for i in range(len(data)):
                # Set timestamp in UTC from field 0 of infile.
                timestamp = datetime.datetime.utcfromtimestamp(
                    float(data[i].split()[0]))
                # Write to outfile if year, month, and day match.
                if timestamp.strftime('%Y-%m-%d') == date.strftime('%Y-%m-%d'):
                    # Append newline to each line before writing to file.
                    outfile.write(data[i] + '\n')
            outfile.close()
        date += datetime.timedelta(days=1)
    return


def main():
    """
    Creates ticker plant directories and populates
    appropriate directories therein.

    """
    # Define parser and collect command line arguments.
    parser = argparse.ArgumentParser(description='Load tick files.')
    parser.add_argument('--group',
                        choices=['equities', 'futures', 'fx'],
                        default='equities',
                        dest='group',
                        help='One of: equities, futures, or fx'
                            ' (default: %(default)s)')
    parser.add_argument('--source',
                        choices=['ib'],
                        default='ib',
                        dest='source',
                        help='One of: ib'
                            ' (default: %(default)s)')
    parser.add_argument('--start',
                        default='2011-11-01',
                        dest='start',
                        help='Date string format %%Y-%%m-%%d'
                            ' (default: %(default)s)')
    parser.add_argument('--end',
                        default='2011-11-02',
                        dest='end',
                        help='Date string format %%Y-%%m-%%d'
                             ' (default: %(default)s)')

    # Read configuration file.
    config = configobj.ConfigObj(os.path.join(
                                              os.getenv('BICYCLE_HOME'),
                                              'config.ini'))

    # Set group.
    group = parser.parse_args().group

    # Set data source for asset class.
    source = parser.parse_args().source

    # Set list of exchanges for asset class and data source.
    exchanges = [key for key in config[group][source].iterkeys()]

    # Set symbols dict keyed on exchange.
    symbols = dict()
    for key in config[group][source].iterkeys():
        symbols[key] = config[group][source][key]

    # Set start and end dates.
    start = datetime.datetime.strptime(parser.parse_args().start, '%Y-%m-%d')
    end = datetime.datetime.strptime(parser.parse_args().end, '%Y-%m-%d')

    # Loop over exchanges.
    for exchange in exchanges:
        # Loop over symbols.
        for symbol in symbols[exchange]:
            expiry = []
            # Read expiry file for each symbol for futures.
            if group == 'futures':
                expiry = read_file(os.path.join('/home/bicycle/tmp', group),
                                                symbol +
                                                '.expiry')
                # Loop over expiry entries for each symbol.
                for contract in expiry:
                    # Read ticks from file if non-zero size.
                    if os.stat(os.path.join(
                                            '/home/bicycle/tmp',
                                            group,
                                            symbol +
                                            contract +
                                            '.tks')).st_size != 0:
                        data = read_file(os.path.join('/home/bicycle/tmp', group),
                                                      symbol +
                                                      contract +
                                                      '.tks')
                        # Set path for writing tick files.
                        path = os.path.join(os.getenv('TICKS_HOME'),
                                            group,
                                            source,
                                            exchange,
                                            symbol,
                                            contract)
                        # Write tick data to files.
                        print 'Writing ticks for symbol {0}' \
                              '  contract {1}'.format(symbol, contract)
                        write_ticks(start,
                                    end,
                                    symbol,
                                    data,
                                    path)
            else:
                # Read ticks from file if non-zero size.
                if os.stat(os.path.join(
                                        '/home/bicycle/tmp',
                                        group,
                                        symbol +
                                        '.tks')).st_size != 0:
                    data = read_file(os.path.join('/home/bicycle/tmp', group),
                                                  symbol +
                                                  '.tks')
                    # Set path for writing tick files.
                    path = os.path.join(os.getenv('TICKS_HOME'),
                                        group,
                                        source,
                                        exchange,
                                        symbol)
                    # Write tick data to files.
                    write_ticks(start,
                                end,
                                symbol,
                                data,
                                path)


if __name__ == '__main__':
    main()
