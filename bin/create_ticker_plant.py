#!/usr/bin/env python
"""Read tick files and create ticker plant.

Command line arguments:
--group : asset class (futures, equities, or fx)
--source : data source (ib)
--start : start date and time (2011-11-01 00:00:00)
--end : end date and time (2011-11-02 00:00:00)

"""

import argparse
import bisect
import configobj
import datetime
import os
import sys

__author__ = "Todd Minehardt"
__copyright__ = "Copyright 2011, 2012 bicycle trading, llc"
__email__ = "todd@bicycletrading.com"


HOLIDAYS = []
with open('/home/bicycle/bicycletrading/share/dates/holidays.txt', 'r') as fn:
    HOLIDAYS = fn.readlines()
HOLIDAYS = [line.strip() for line in HOLIDAYS]


def check_date(date):
    """
    Returns True if date is not a Saturday or Sunday or
    holiday, False otherwise.

    """
    if (date.weekday() < 5) and (date.strftime('%Y-%m-%d') not in HOLIDAYS):
        return True
    else:
        return False


def find_ge(values, threshold):
    """Return index for leftmost value => threshold."""
    i = bisect.bisect_left(values, threshold)
    if i != len(values):
        return i
    else:
        raise ValueError


def find_le(values, threshold):
    """Return index for rightmost value > threshold."""
    i = bisect.bisect_right(values, threshold)
    if i:
        return i
    else:
        raise ValueError


def get_subset(index, values, threshold):
    """
    Return subset of values for a given threshold by indexing on index.

    Start time is set as threshold: year, month, day, 0, 0, 0.
    End time is set as threshold: year, month, day + 1 day, 0, 0, 0.

    """
    start_time = datetime.datetime.combine(threshold, datetime.time(0, 0, 0))
    start_idx = find_ge(index, start_time)
    end_time = datetime.datetime.combine(threshold +
                                         datetime.timedelta(days=1),
                                         datetime.time(0, 0, 0))
    end_idx = find_le(index, end_time)
    values = values[start_idx:end_idx]
    return values


def get_timestamps(data):
    """Return list of sorted timestamps from first column of data."""
    values = []
    for i in range(len(data)):
        values.append(datetime.datetime.utcfromtimestamp(
            float(data[i].split()[0])))
    values.sort()
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
    with open(filename, 'r') as infile:
        values = infile.readlines()
    values = [i.strip() for i in values]
    return values


def set_exchanges_symbols(config, group, source):
    """Returns exchanges list and symbols dict as pair of tuples."""
    exchanges = [key for key in config[group][source].iterkeys()]
    symbols = {}
    if group == 'equities':
        symbol_file = {}
        for key in config[group][source].iterkeys():
            symbol_file[key] = config[group][source][key]
            with open(symbol_file[key], 'r') as infile:
                symbol_list = infile.readlines()
            symbols[key] = [i.strip() for i in symbol_list]
    else:
        for key in config[group][source].iterkeys():
            symbols[key] = config[group][source][key]
    return exchanges, symbols


def set_parser():
    """Return parser for command line arguments."""
    values = argparse.ArgumentParser(description='Create ticker plant.')
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
                        help='One of: ib'
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
    Return tuple of start and end dates modifed if data start
    and/or times are before/after start/end.
    """
    first = datetime.datetime.utcfromtimestamp(float(
                                               data[0].split()[0])).date()
    last = datetime.datetime.utcfromtimestamp(float(
                                              data[-1].split()[0])).date()
    start = start.date()
    end = end.date()
    if first:
        start = first
    if last < end:
        end = last
    return start, end


def write_ticks(start, end, symbol, data, path):
    """Write ticks to files with .tks suffix."""
    # Extract list of timestamps from data.
    timestamps = get_timestamps(data)
    # Adjust beginning ('now') and end ('end') if needed.
    now, then = set_start_end(start, end, data)
    while now <= then:
        # Make sure date is not on a weekend or holiday.
        if check_date(now):
            # Extract subset of data for this day only.
            subset = get_subset(timestamps, data, now)
            # Set directory for writing ticks; create if required.
            outdir = os.path.join(path,
                                  '{0:04d}'.format(now.year),
                                  '{0:02d}'.format(now.month),
                                  '{0:02d}'.format(now.day))
            if not os.path.isdir(outdir):
                os.makedirs(outdir, 0755)
            # Set tks file for output.
            tks = os.path.join(outdir, symbol + '.tks')
            # Create outfile in append mode.
            with open(tks, 'a') as outfile:
                for i in range(len(subset)):
                    # Append newline before writing to file.
                    outfile.write(subset[i] + '\n')
        now += datetime.timedelta(days=1)
    return


def main():
    """
    Creates ticker plant directories and populates
    appropriate directories therein. Appends files.

    """
    # Read configuration file.
    config = configobj.ConfigObj(os.path.join(os.getenv('BICYCLE_HOME'),
                                                        'config.ini'))

    # Parse command line arguments, set local variables.
    parser = set_parser()
    group = parser.parse_args().group
    source = parser.parse_args().source
    srcdir = config[group]['srcdir']
    start = parser.parse_args().start
    end = parser.parse_args().end
    start = datetime.datetime.strptime(start, '%Y-%m-%d %H:%M:%S')
    end = datetime.datetime.strptime(end, '%Y-%m-%d %H:%M:%S')
    exchanges, symbols = set_exchanges_symbols(config, group, source)

    # Loop over exchanges and symbols.
    for exchange in exchanges:
        for symbol in symbols[exchange]:
            # Set path for per-symbol expiry file for futures.
            if group == 'futures':
                # Read expiry files if they exist and are non-zero size.
                fname = os.path.join(srcdir, symbol + '.expiry')
                if (os.path.isfile(fname) and os.stat(fname).st_size != 0):
                    expiry = read_file(srcdir, symbol + '.expiry')
                    # Loop over expiry entries for each symbol.
                    for contract in expiry:
                        # Read ticks from file if it exists and is
                        # non-zero size.
                        fname = os.path.join(srcdir,
                                             symbol +
                                             contract +
                                             '.tks')
                        if (os.path.isfile(fname) and
                            os.stat(fname).st_size != 0):
                            data = read_file(srcdir,
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
                            print("Writing ticks for {0}{1}...").format(
                                                                   symbol,
                                                                   contract)
                            write_ticks(start, end, symbol, data, path)
            else:
                # Read ticks from file if it exists and is non-zero size.
                fname = os.path.join(srcdir, symbol + '.tks')
                if (os.path.isfile(fname) and os.stat(fname).st_size != 0):
                    data = read_file(srcdir, symbol + '.tks')
                    # Set path for writing tick files.
                    path = os.path.join(os.getenv('TICKS_HOME'),
                                        group,
                                        source,
                                        exchange,
                                        symbol)
                    # Write tick data to files.
                    print("Writing ticks for {0}...").format(symbol)
                    write_ticks(start, end, symbol, data, path)


if __name__ == '__main__':
    main()
