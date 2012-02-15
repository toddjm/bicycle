#!/usr/bin/env python
"""Gather statistics for entries in the ticker plant."""

import argparse
import collections
import datetime
import os
import sys

__author__ = "Todd Minehardt"
__copyright__ = "Copyright 2011,2012 bicycle trading, llc"
__email__ = "todd@bicycletrading.com"


def get_dates_from_dir(path):
    """Return list of namedtuples for year, month, and days given dir path."""
    if not os.path.isdir(path):
        print("Directory {0} does not exist.").format(path)
        sys.exit()
    date = collections.namedtuple('date', ['year', 'month', 'days'])
    values = []
    days = {}
    months = {}
    years = [x for x in os.listdir(path)]
    for i in years:
        months[i] = [x for x in os.listdir(os.path.join(path, i))]
        for j in months[i]:
            days[j] = [x for x in os.listdir(os.path.join(path, i, j))]
            values.append(date(i, j, days[j]))
    return values


def get_futures_stats(exchanges, symbols, expiry, root):
    """Writes to stdout statistics for futures ticks."""
    for i in exchanges:
        for j in symbols[i]:
            for k in expiry[j]:
                values = get_tks_data(root, i, j, k)
                for l in range(len(values)):
                    print(values[l])
    return

def get_tks_data(root, i, j, k):
    """Return list of namedtuples for tks files in root dir."""
    data = collections.namedtuple('data', ['exchange', 'symbol', 'expiry',
                                           'year', 'month', 'day', 'first',
                                           'last', 'number'])
    values = []
    days = {}
    months = {}
    years = {}
    cwd = os.path.join(root, i, j, k)
    years[k] = [x for x in os.listdir(cwd)]
    for year in years[k]:
        months[year] = [x for x in os.listdir(os.path.join(
                                              cwd, year))]
        for month in months[year]:
            days[month] = [x for x in os.listdir(os.path.join(
                                                 cwd, year, month))]
            for day in days[month]:
                infile = os.path.join(cwd, year, month, day,
                                      j + '.tks')
                if not os.stat(infile).st_size == 0:
                    with open(infile, 'r') as tmp:
                        tks = tmp.readlines()
                    tks = [x.strip() for x in tks]
                    first = datetime.datetime.utcfromtimestamp(
                        float(tks[0].split()[0]))
                    last = datetime.datetime.utcfromtimestamp(
                        float(tks[-1].split()[0]))
                    values.append(data(i, j, k, year, month, day, first, last,
                                       len(tks)))
    return values


def read_file(path, name):
    """Read from file and return a list of strings without newlines."""
    if not os.path.isdir(path):
        print("Directory {0} does not exist.").format(path)
        sys.exit()
    if not os.path.isfile(os.path.join(path, name)):
        print("File {0} does not exist.").format(name)
    try:
        infile = open(os.path.join(path, name), 'r')
    except IOError:
        print("File {0} does not exist.").format(infile)
        sys.exit()
    values = infile.readlines()
    values = [x.strip() for x in values]
    infile.close()
    return values


# Read holidays list from file.
HOLIDAYS = []
HOLIDAYS = read_file(os.path.join(
                                  os.getenv('BICYCLE_HOME'),
                                  'share/dates'),
                                  'holidays.txt')


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


def write_ticks(start, end, symbol, data, path):
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
                print("File {0} cannot be created.").format(outfile)
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
    Searches ticker plant directories and outputs
    statistics for what is collected and missing.

    """
    # Define parser and collect command line arguments.
    parser = argparse.ArgumentParser(description='Analyze ticker plant.')
    parser.add_argument('--group',
                        default='futures',
                        dest='group',
                        help='One of: equities, fx, or futures '
                             '(default: %(default)s)',
                        nargs='?')
    parser.add_argument('--source',
                        default='ib',
                        dest='source',
                        help='Default: %(default)s)')
    parser.add_argument('--exchanges',
                        default='nymex',
                        dest='exchanges',
                        help='Space-separated names (default: %(default)s)',
                        nargs='+')
    parser.add_argument('--start',
                        default='2011-11-01',
                        dest='start',
                        help='Date format %%Y-%%m-%%d (default: %(default)s)')
    parser.add_argument('--end',
                        default='2011-11-02',
                        dest='end',
                        help='Date format %%Y-%%m-%%d (default: %(default)s)')

    # Set group and source.
    group = parser.parse_args().group
    source = parser.parse_args().source

    # Set root directory.
    root = os.path.join(os.getenv('TICKS_HOME'), group, source)

    # Set exchanges based on group and source if not specified.
    exchanges = []
    exchanges = parser.parse_args().exchanges
    if not exchanges:
        exchanges = os.listdir(root)

    # Set symbols and, for futures, expiry.
    if group == 'futures':
        expiry = {}

    symbols = {}
    for i in exchanges:
        symbols[i] = [x for x in os.listdir(os.path.join(root, i))]
        if group == 'futures':
            for j in symbols[i]:
                expiry[j] = os.listdir(os.path.join(root, i, j))

    values = get_futures_stats(exchanges, symbols, expiry, root)
    for i in range(len(values)):
        print(values[i])


if __name__ == '__main__':
    main()
