#!/usr/bin/env python
"""Read tick files and create ticker plant.

Command line arguments:
group -- asset class (futures, equities, or fx)
source -- data source (ib)
start -- start date (2009-09-01)
end -- end date (2011-11-01)

"""

import argparse
import bisect
import configobj
import datetime
import os
import sys

__author__ = "Todd Minehardt"
__copyright__ = "Copyright 2011, bicycle trading, llc"
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
    # Ensure that date is not a Saturday, Sunday, or holiday.
    if (date.weekday() < 5) and (date.strftime('%Y-%m-%d') not in HOLIDAYS):
        return True
    return False


def find_start_idx(timestamps, date):
    """Return index from timestamps where timestamps[index] >= date.
    Equivalent to finding rightmost element in timestamps <= date.
    """
    i = bisect.bisect_left(timestamps, date)
    if i != len(timestamps):
        return i
    raise ValueError


def find_end_idx(timestamps, date):
    """
    Return index from timestamps where timestamps[index] < date.
    Equivalent to finding leftmost element in timestamps >= date.
    """
    i = bisect.bisect_right(timestamps, date)
    if i:
        return i - 1
    raise ValueError


def get_subset(timestamps, data, date):
    """
    Return subset of data by indexing into it using timestamps
    for the 1-day period of interest ('date').
    'start_idx' is the index number in timestamps for which the
    first instance of timestamps[index] >= date is true.
    'end_idx' is the index number in timestamps for which the
    first instance of timestamps[index] >= (date + 1 day) is true.
    """
    # Start where timestamps[index] >= date.
    start_idx = find_start_idx(timestamps, date)
    # End where timestamps[index] >
    end_idx = find_end_idx(timestamps, date + datetime.timedelta(days=1))
    #print('date = {0} start_idx = {1} end_idx = {2}').format(date, start_idx,
    #                                                         end_idx)
    # Extract subset of data for this date.
    #subset = data[start_idx:end_idx]
    #return subset
    return  data[start_idx:end_idx]


def get_timestamps(data):
    """Return list of timestamps from first column of data."""
    timestamps = []
    for i in range(len(data)):
        timestamps.append(datetime.datetime.utcfromtimestamp(
            float(data[i].split()[0])))
    return timestamps


def read_file(path, name):
    """Read from file and return a list of strings without newlines."""
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
    """Returns exchanges list and symbols dict as tuple."""
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


def set_start_end(start, end, data):
    """
    Return tuple of start and end times modifed if data start
    and/or times are before/after start/end.
    """
    first = datetime.datetime.utcfromtimestamp(float(data[0].split()[0]))
    last = datetime.datetime.utcfromtimestamp(float(data[-1].split()[0]))
    if first > start:
        start = first
    if last < end:
        end = last
    return start, end


def write_ticks(start, end, symbol, data, path):
    """Write ticks to files with .tks suffix."""
    # Extract list of timestamps from data.
    timestamps = get_timestamps(data)
    # Adjust beginning ('now') and end ('end') if needed.
    now, end = set_start_end(start, end, data)
    #print('start = {0} end = {1}').format(now, end)
    while now <= end:
        # Make sure date is not on a weekend or holiday.
        if check_date(now):
            # Extract subset of data for 'now.'
            #print('now = {0} end = {1}').format(now, end)
            subset = get_subset(timestamps, data, now)
            # Set directory for writing ticks; create if required.
            outdir = os.path.join(path,
                                  '{0:04d}'.format(now.year),
                                  '{0:02d}'.format(now.month),
                                  '{0:02d}'.format(now.day))
            if not os.path.isdir(outdir):
                os.makedirs(outdir, 0755)
            # Set .tks file for output.
            tksfile = os.path.join(outdir, symbol + '.tks')
            # Create outfile in append mode.
            with open(tksfile, 'a') as outfile:
                for i in range(len(subset)):
                    # Append newline to each line before writing to file.
                    outfile.write(subset[i] + '\n')
        now += datetime.timedelta(days=1)
    return


def main():
    """
    Creates ticker plant directories and populates
    appropriate directories therein.

    """
    # Read configuration file.
    config = configobj.ConfigObj(os.path.join(os.getenv('BICYCLE_HOME'),
                                                        'config.ini'))

    # Define parser and collect command line arguments.
    parser = argparse.ArgumentParser(description='Load ticker plant.')
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
                        default='2011-11-01 00:00:00',
                        dest='start',
                        help='Date string format %%Y-%%m-%%d %%H:%%M:%%S'
                            ' (default: %(default)s)')
    parser.add_argument('--end',
                        default='2011-11-02 00:00:00',
                        dest='end',
                        help='Date string format %%Y-%%m-%%d %%H:%%M:%%S'
                             ' (default: %(default)s)')

    # Set group.
    group = parser.parse_args().group

    # Set data source for asset class.
    source = parser.parse_args().source

    # Set source directory for files to read and convert.
    srcdir = config[group]['srcdir']

    # Set exchanges and symbols.
    exchanges, symbols = set_exchanges_symbols(config, group, source)

    # Set start time as UTC (e.g. 2009-09-01 == 2009-09-01 00:00:00).
    start = datetime.datetime.strptime(parser.parse_args().start,
                                       '%Y-%m-%d %H:%M:%S')

    # Set end time as UTC (e.g. 2010-09-02 == 2010-09-02 00:00:00).
    end = datetime.datetime.strptime(parser.parse_args().end,
                                     '%Y-%m-%d %H:%M:%S')

    # Loop over exchanges and symbols.
    for exchange in exchanges:
        for symbol in symbols[exchange]:
            # Set path for per-symbol expiry file for futures.
            if group == 'futures':
                expiry = read_file(srcdir, symbol + '.expiry')
                # Loop over expiry entries for each symbol.
                for contract in expiry:
                    # Read ticks from file if non-zero size.
                    if os.stat(os.path.join(srcdir,
                                            symbol +
                                            contract +
                                            '.tks')).st_size != 0:
                        data = read_file(srcdir, symbol + contract + '.tks')
                        # Set path for writing tick files.
                        path = os.path.join(os.getenv('TICKS_HOME'),
                                            group,
                                            source,
                                            exchange,
                                            symbol,
                                            contract)
                        # Write tick data to files.
                        print("Writing ticks for {0}{1}...").format(symbol,
                                                                    contract)
                        write_ticks(start, end, symbol, data, path)
            else:
                # Read ticks from file if non-zero size.
                if os.stat(os.path.join(srcdir, symbol + '.tks')).st_size != 0:
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
