#!/usr/bin/env python
"""Gather statistics for entries in the ticker plant."""

import argparse
import datetime
import os
import sys

__author__ = "Todd Minehardt"
__copyright__ = "Copyright 2011,2012 bicycle trading, llc"
__email__ = "todd@bicycletrading.com"


def check_date(date):
    """
    Returns True if date is not a Saturday or Sunday or
    holiday, False otherwise.
    """
    holidays = get_holidays()
    # Ensure that date is not a Saturday, Sunday, or holiday.
    if (date.weekday() < 5) and (date.strftime('%Y-%m-%d') not in holidays):
        return True
    else:
        return False


def get_holidays():
    """Read holidays list from file."""
    infile = os.path.join(os.getenv('BICYCLE_HOME'),
                                    'share/dates/holidays.txt')
    with open(infile, 'r') as tmp:
        holidays = tmp.readlines()
    holidays = [x.strip() for x in holidays]
    return holidays


def get_tks_data(root, **kwargs):
    """Return list of stats for tks files in root dir."""
    exchange = kwargs.get('exchange', "")
    expiry = kwargs.get('expiry', "")
    symbol = kwargs.get('symbol', "")
    cwd = os.path.join(root, exchange, symbol, expiry)
    values = []
    for year in os.listdir(cwd):
        for month in os.listdir(os.path.join(cwd, year)):
            for day in os.listdir(os.path.join(cwd, year, month)):
                infile = os.path.join(cwd, year, month, day, symbol + '.tks')
                if not os.stat(infile).st_size == 0:
                    with open(infile, 'r') as tmp:
                        tks = tmp.readlines()
                    tks = [x.strip() for x in tks]
                    values.append([exchange,
                                   symbol + expiry,
                                   year,
                                   month,
                                   day,
                                   datetime.datetime.utcfromtimestamp(
                                   float(tks[0].split()[0])).strftime(
                                   '%Y/%m/%d %H:%M:%S'),
                                   datetime.datetime.utcfromtimestamp(
                                   float(tks[-1].split()[0])).strftime(
                                   '%Y/%m/%d %H:%M:%S'),
                                   len(tks)])
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


def set_expiry(root, exchanges, symbols):
    """Return dict for expiry, keyed on symbols."""
    expiry = {}
    for i in exchanges:
        for j in symbols[i]:
            expiry[j] = os.listdir(os.path.join(root, i, j))
    return expiry


def set_parser():
    """Return parser for command line arguments."""
    parser = argparse.ArgumentParser(description='Analyze ticker plant.')
    parser.add_argument('--group',
                        default='futures',
                        dest='group',
                        help='One of: equities, fx, or futures '
                             '(default: %(default)s)',
                        nargs=1)
    parser.add_argument('--source',
                        default='ib',
                        dest='source',
                        help='Default: %(default)s)',
                        nargs=1)
    parser.add_argument('--exchanges',
                        default='nymex',
                        dest='exchanges',
                        help='Space-separated names (default: %(default)s)',
                        nargs='+')
    return parser


def set_symbols(root, exchanges):
    """Return dict of symbols, keyed on exchanges."""
    symbols = {}
    for i in exchanges:
        symbols[i] = os.listdir(os.path.join(root, i))
    return symbols


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
    # Parse command line arguments.
    parser = set_parser()

    # Set group, source, and exchanges.
    group = parser.parse_args().group[0]
    source = parser.parse_args().source[0]
    exchanges = parser.parse_args().exchanges

    print(group)
    print(source)
    print(exchanges)

    # Set root directory.
    root = os.path.join(os.getenv('TICKS_HOME'), group, source)

    print(root)

    # Set symbols and expiry dicts.
    symbols = set_symbols(root, exchanges)
    expiry = set_expiry(root, exchanges, symbols)

    for exchange in exchanges:
        for symbol in symbols[exchange]:
            for expiration in expiry[symbol]:
                values = get_tks_data(root,
                                      exchange=exchange,
                                      symbol=symbol,
                                      expiry=expiration)
                print(values)


if __name__ == '__main__':
    main()
