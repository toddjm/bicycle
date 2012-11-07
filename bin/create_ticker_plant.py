#!/usr/bin/python
"""Read tick files and create ticker plant.

Command line arguments:
--group : asset class (futures, equities, or fx)
--source : data source (ib)
--start : start date and time (2011-11-01 00:00:00)
--end : end date and time (2011-11-02 00:00:00)

"""

import argparse
import bisect
import bz2
import configobj
import datetime
import os
import sys

__author__ = "Todd Minehardt"
__copyright__ = "Copyright 2011, 2012 bicycle trading, llc"
__email__ = "todd@bicycletrading.com"


def holidays():
    """Return holiday dates from text file."""
    infile = os.path.join(os.getenv('BICYCLE_HOME'),
                          'share/dates/holidays.txt')
    with open(infile, 'r') as tmp:
        values = tmp.readlines()
    values = [i.strip() for i in values]
    return values


HOLIDAYS = holidays()


def check_date(date):
    """
    Returns True if date is not a Saturday or Sunday or
    holiday, False otherwise.

    """
    if (date.weekday() < 5) and (date.strftime('%Y-%m-%d') not in HOLIDAYS):
        return True
    return False


def create_tks_files(config, options):
    """Read source files, write tks files."""
    group = options.parse_args().group
    source = options.parse_args().source
    start = options.parse_args().start
    end = options.parse_args().end
    start = datetime.datetime.strptime(start, '%Y-%m-%d %H:%M:%S')
    end = datetime.datetime.strptime(end, '%Y-%m-%d %H:%M:%S')
    srcdir = config[group]['root']  # like /home/bicycle/tmp/futures
    exchanges = set_exchanges(config, group, source)
    if group == 'futures':
        symbols = set_symbols(config, group, source)
        for exchange in exchanges:
            expiry = get_expiry(srcdir, symbols[exchange])
            for symbol in expiry.keys():  # filters-out unlisted symbols
                for contract in expiry[symbol]:
                    data = read_tks_file(srcdir, symbol, contract=contract)
                    path = os.path.join(os.getenv('TICKS_HOME'), group,
                                        source, exchange, symbol, contract)
                    print("Writing ticks for {0}{1}...").format(symbol,
                                                                contract)
                    write_tks_file(start, end, symbol, data, path)
    else:
        symbols = get_symbols(srcdir)
        for exchange in exchanges:
            for symbol in symbols:
                data = read_tks_file(srcdir, symbol)
                path = os.path.join(os.getenv('TICKS_HOME'), group, source,
                                    exchange, symbol)
                print("Writing ticks for {0}...").format(symbol)
                write_tks_file(start, end, symbol, data, path)
    return


def find_ge(values, threshold):
    """Return index for leftmost value => threshold."""
    i = bisect.bisect_left(values, threshold)
    if i != len(values):
        return i
    raise ValueError


def find_le(values, threshold):
    """Return index for rightmost value > threshold."""
    i = bisect.bisect_right(values, threshold)
    if i:
        return i
    raise ValueError


def get_expiry(srcdir, symbols):
    """Returns a dict of contract expirations keyed on symbol."""
    values = {}
    for i in symbols:
        infile = os.path.join(srcdir, i + '.expiry')
        if os.path.isfile(infile) and os.path.getsize(infile):
            values[i] = read_file(srcdir, i + '.expiry')
    return values


def get_subset(values, threshold):
    """
    Return subset of values, indexed on first column, for a given threshold.

    Start time is set as threshold: year, month, day, 0, 0, 0.
    End time is set as threshold: year, month, day + 1 day, 0, 0, 0.

    """
    subset = []
    index = [datetime.datetime.utcfromtimestamp(float(i.split()[0]))
             for i in values]
    s_time = datetime.datetime.combine(threshold, datetime.time(0, 0, 0))
    s_indx = find_ge(index, s_time)
    e_time = datetime.datetime.combine(threshold +
                                       datetime.timedelta(days=1),
                                       datetime.time(0, 0, 0))
    e_indx = find_le(index, e_time)
    subset = values[s_indx:e_indx]
    return subset


def get_symbols(srcdir):
    """Get symbols for which tks files are non-zero length."""
    values = []
    for i in os.listdir(srcdir):
        if i.endswith('.tks'):
            values.append(i.strip('.tks'))
    return values


def read_file(path, name):
    """Read file and return a list of strings without newlines."""
    if not os.path.isdir(path):
        print("{0} is not a directory.").format(path)
        sys.exit()
    if not os.path.isfile(os.path.join(path, name)):
        print("{0} is not a file.").format(name)
        sys.exit()
    filename = os.path.join(path, name)
    values = []
    with open(filename, 'r') as infile:
        values = infile.readlines()
    values = [i.strip() for i in values]
    return values


def get_exchanges_symbols(config, group, source):
    """Returns exchanges list and symbols dict as tuple."""
    exchanges = [i for i in config[group][source].iterkeys()]
    symbols = {}
    if group == 'equities':
        symbol_file = {}
        for i in config[group][source].iterkeys():
            symbol_file[i] = config[group][source][i]
            with open(symbol_file[i], 'r') as infile:
                symbol_list = infile.readlines()
            symbols[i] = [i.strip() for i in symbol_list]
    else:
        for i in config[group][source].iterkeys():
            symbols[i] = config[group][source][i]
    return exchanges, symbols


def read_tks_file(srcdir, symbol, **kwargs):
    """Read tks file, return list sorted on timestamp. """
    contract = kwargs.get('contract', "")
    infile = os.path.join(srcdir, symbol + contract + '.tks')
    if os.path.isfile(infile) and os.path.getsize(infile):
        values = read_file(srcdir, symbol + contract + '.tks')
    return sorted(values, key=lambda x: x[0])


def set_exchanges(config, group, source):
    """Return list of exchanges."""
    values = []
    values = [i for i in config[group][source].iterkeys()]
    return values


def set_parser():
    """Return parser for command line arguments."""
    values = argparse.ArgumentParser(description='Create ticks files.')
    values.add_argument('--group',
                        choices=['equities', 'futures', 'fx'],
                        default='equities',
                        dest='group',
                        help='One of: %(choices)s '
                             '(default: %(default)s)')
    values.add_argument('--source',
                        choices=['ib'],
                        default='ib',
                        dest='source',
                        help='One of: ib '
                             '(default: %(default)s)')
    values.add_argument('--start',
                        default='2011-11-01 00:00:00',
                        dest='start',
                        help='Date string format %%Y-%%m-%%d %%H:%%M:%%S '
                             '(default: %(default)s)')
    values.add_argument('--end',
                        default='2011-11-02 00:00:00',
                        dest='end',
                        help='Date string format %%Y-%%m-%%d %%H:%%M:%%S '
                             '(default: %(default)s)')
    return values


def set_start_end(start, end, data):
    """
    Return tuple of start/end date modifed if data first (last)
    date is after (before) start (end) date given by user.

    """
    first = datetime.datetime.utcfromtimestamp(
            float(data[0].split()[0])).date()
    last = datetime.datetime.utcfromtimestamp(
            float(data[-1].split()[0])).date()
    start = start.date()
    end = end.date()
    if first > start:
        start = first
    if last < end:
        end = last
    return start, end


def set_symbols(config, group, source):
    """Returns dict of symbols keyed on exchanges."""
    values = {}
    if group == 'equities':
        symbol_file = {}
        for i in config[group][source].iterkeys():
            symbol_file[i] = config[group][source][i]
            with open(symbol_file[i], 'r') as infile:
                symbol_list = infile.readlines()
            values[i] = [i.strip() for i in symbol_list]
    else:
        for i in config[group][source].iterkeys():
            values[i] = config[group][source][i]
    return values


def write_tks_file(start, end, symbol, data, path):
    """Write ticks to files with .tks suffix."""
    # Adjust beginning ('now') and end ('end') if needed.
    now, then = set_start_end(start, end, data)
    while now <= then:
        # Make sure date is not on a weekend or holiday.
        if check_date(now):
            # Extract subset of data for this day only.
            subset = get_subset(data, now)
            if subset:
                # Set directory for writing ticks, create if needed.
                outdir = os.path.join(path,
                                      '{0:04d}'.format(now.year),
                                      '{0:02d}'.format(now.month),
                                      '{0:02d}'.format(now.day))
                if not os.path.isdir(outdir):
                    os.makedirs(outdir, 0755)
                    tks = os.path.join(outdir, symbol + '.tks.bz2')
                    #if not os.path.isfile(tks):
                    #    outfile = bz2.BZ2File(tks, 'wb')
                    #    try:
                    #        for i in subset:
                    #            outfile.write(i + '\n')
                    #    finally:
                    #        outfile.close()
                    outfile = bz2.BZ2File(tks, 'wb')
                    try:
                        for i in subset:
                            outfile.write(i + '\n')
                    finally:
                        outfile.close()
        now += datetime.timedelta(days=1)
    return


def main():
    """
    Creates ticker plant directories and populates
    appropriate directories therein.

    """
    # Read configuration file, parse command line arguments.
    config = configobj.ConfigObj(os.path.join(os.getenv('BICYCLE_HOME'),
                                              'config.ini'))
    parser = set_parser()

    create_tks_files(config, parser)


if __name__ == '__main__':
    main()
