#!/usr/bin/env python
"""Gather statistics for entries in the ticker plant."""

import argparse
import collections
import datetime
import os
import sys

__author__ = "Todd Minehardt"
__copyright__ = "Copyright 2011, bicycle trading, llc"
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
    for year in years:
        months[year] = [x for x in os.listdir(os.path.join(path,
                                                           year))]
        for month in months[year]:
            days[month] = [x for x in os.listdir(os.path.join(path,
                                                              year,
                                                              month))]
            values.append(date(year, month, days[month]))
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
                        choices=['equities', 'futures', 'fx'],
                        default='equities',
                        dest='group',
                        help='One of: {0} ' \
                             '(default: %(default)s)'.format(choices),
                        nargs='?')
    parser.add_argument('--source',
                        choices='ib',
                        default='ib',
                        dest='source',
                        help='One of: {0} ' \
                             '(default: %(default)s)'.format(choices))
    parser.add_argument('--exchanges',
                        default='smart',
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

def setup_vars(parser):
    """Return namedtuple of config variables based on user input."""
    if not parser:
        print("Parser not found, exiting...")
        sys(exit)

    # Set group and source.
    group = parser.parse_args().group
    source = parser.parse_args().source

    # Set root directory.
    root = os.path.join(os.getenv('TICKS_HOME'), group, source)

    # Set exchanges based on group and source if not specified.
    exchanges = parser.parse_args().exchanges.split()
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

    # Set config file.
    if group == 'futures': 
        config = collections.namedtuple('config',
                                        ['root',
                                         'exchanges',
                                         'symbols',
                                         'expiry'])
        return config(root, exchanges, symbols, expiry)
    else:
        config = collections.namedtuple('config',
                                        ['root',
                                         'exchanges',
                                         'symbols'])
        return config(root, exchanges, symbols)


    data = []
    years = {}
    months = {}
    days = {}
    for i in exchanges:
        for j in symbols[i]:
            for k in expiry[j]:
                cwd = os.path.join(root, i, j, k)
                years[k] = [x for x in os.listdir(cwd)]
                for y_k in years[k]:
                    months[y_k] = [x for x in os.listdir(
                        os.path.join(cwd, y_k))]
                    for m_y_k in months[y_k]:
                        days[m_y_k] = [x for x in os.listdir(
                            os.path.join(cwd, y_k, m_y_k))]
                        for d_m_y_k in days[m_y_k]:
                            infile = os.path.join(cwd,
                                                  y_k,
                                                  m_y_k,
                                                  d_m_y_k,
                                                  j + '.tks')
                            if not os.stat(infile).st_size == 0:
                                with open(infile, 'r') as tmp:
                                    ticks = tmp.readlines()
                                ticks = [x.strip() for x in ticks]
                                first = datetime.datetime.utcfromtimestamp(
                                    float(ticks[0].split()[0]))
                                last = datetime.datetime.utcfromtimestamp(
                                    float(ticks[-1].split()[0]))
                                print i, j, k, y_k, m_y_k, d_m_y_k, \
                                      first, last, len(ticks)
                                data.append(contract(i, j, k,
                                                     y_k, m_y_k, d_m_y_k,
                                                     first, last, len(ticks)))



if __name__ == '__main__':
    main()
