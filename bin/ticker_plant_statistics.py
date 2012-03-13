#!/usr/bin/env python
"""Gather statistics for entries in the ticker plant."""

import argparse
import bisect
import collections
import datetime
import os

__author__ = "Todd Minehardt"
__copyright__ = "Copyright 2011, 2012 bicycle trading, llc"
__email__ = "todd@bicycletrading.com"


class Holiday(object):
    """Holidays class."""
    infile = os.path.join(os.getenv('BICYCLE_HOME'),
                                    'share/dates/holidays.txt')
    with open(infile, 'r') as tmp:
        values = tmp.readlines()
    values = [i.strip() for i in values]
    holidays = values


HOLIDAYS = Holiday.holidays


def check_date(date):
    """
    Returns True if date is weekday/non-holiday, False otherwise. Expects
    date as type(datetime.datetime).

    """
    # Ensure that date is not a Saturday, Sunday, or holiday.
    if (date.weekday() < 5) and (date.strftime('%Y-%m-%d') not in HOLIDAYS):
        return True
    return False


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


def find_duplicates(root, **kwargs):
    """
    Return list of full path names to tick files containing
    duplicate entries.

    """
    exchange = kwargs.get('exchange', "")
    expiry = kwargs.get('expiry', "")
    symbol = kwargs.get('symbol', "")
    cwd = os.path.join(root, exchange, symbol, expiry)
    duplicates = []
    for year in os.listdir(cwd):
        for month in os.listdir(os.path.join(cwd, year)):
            for day in os.listdir(os.path.join(cwd, year, month)):
                infile = os.path.join(cwd, year, month, day, symbol + '.tks')
                if not os.stat(infile).st_size == 0:
                    files = get_duplicates(infile)
                    for i in range(len(files)):
                        if (str(files[i]) is not None):
                            duplicates.append(files[i])
    return duplicates


#def get_duplicates(values):
#    values = get_timestamps(values)
#    counter = collections.Counter(values)
#    for i in counter:
#        if counter[i] > 1:
#            break
#        return True
#    return False
def get_duplicates(infile):
    """Return list of paths to files containing duplicates."""
    with open(infile, 'r') as tmp:
        tks = tmp.readlines()
    tks = [i.strip() for i in tks]
    tmp.close()
    files = []
    values = []
    for i in range(len(tks)):
        values.append(datetime.datetime.utcfromtimestamp(
            float(tks[i].split()[0])))
    values.sort()
    counter = collections.Counter(values)
    for i in counter:
        if counter[i] > 1:
            files.append(infile)
    return files


def get_start_end_datetime(tks):
    """Return tuple of start and end times for a tks file."""
    start = datetime.datetime.utcfromtimestamp(
             float(tks[0].split()[0])).strftime('%Y/%m/%d %H:%M:%S')
    end = datetime.datetime.utcfromtimestamp(
           float(tks[-1].split()[0])).strftime('%H:%M:%S')
    return start, end


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


def get_tks_datetime(root, **kwargs):
    """
    Return list of date, start time, and end time for tks files
    of non-zero size.
    Format is YYYY/MM/DD HH:MM:SS HH:MM:SS where first time and
    last time for each date are second and third fields.

    """
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
                    tks = [i.strip() for i in tks]
                    start, end = get_start_end_datetime(tks)
                    values.append(start + ' ' + end)
    return values


def read_ticks_files(root, **kwargs):
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
                    tks = [i.strip() for i in tks]
                    tmp.close()
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


def set_expiry(root, exchanges, symbols):
    """Return dict for expiry, keyed on symbols."""
    values = {}
    for i in exchanges:
        for j in symbols[i]:
            values[j] = os.listdir(os.path.join(root, i, j))
    return values


def set_parser():
    """Return parser for command line arguments."""
    values = argparse.ArgumentParser(description='Analyze ticker plant.')
    values.add_argument('--group',
                        choices=['equities', 'futures', 'fx'],
                        default='futures',
                        dest='group',
                        help='One of: %(choices)s '
                             '(default: %(default)s)')
    values.add_argument('--source',
                        choices=['ib'],
                        default='ib',
                        dest='source',
                        help='Default: %(default)s)')
    # 'exchanges' must be returned as a list, even for one member.
    values.add_argument('--exchanges',
                        choices=['smart', 'idealpro', 'cfe', 'dtb', 'ecbot',
                                 'globex', 'ipe', 'liffe', 'nybot', 'nymex',
                                 'nyseliffe'],
                        default=['nymex'],
                        dest='exchanges',
                        help='Space-separated names (default: %(default)s)',
                        nargs='+')
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


def set_symbols(root, exchanges):
    """Return dict of symbols, keyed on exchanges."""
    values = {}
    for i in exchanges:
        values[i] = os.listdir(os.path.join(root, i))
    return values


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
    Searches ticker plant directories and outputs
    statistics for what is collected and missing.

    """
    # Parse command line arguments, set local variables.
    parser = set_parser()
    group = parser.parse_args().group
    source = parser.parse_args().source
    exchanges = parser.parse_args().exchanges
    root = os.path.join(os.getenv('TICKS_HOME'), group, source)
    symbols = set_symbols(root, exchanges)

    # Print list containing lines such as:
    # [exchange, symbol + expiry, year_collected, month_collected,
    #  day_collected, start_time, end_time, number_of_entries]
    if (group == 'futures'):
        expiry = set_expiry(root, exchanges, symbols)
        for exchange in exchanges:
            for symbol in symbols[exchange]:
                for expiration in expiry[symbol]:
                    values = read_ticks_files(root,
                                              exchange=exchange,
                                              symbol=symbol,
                                              expiry=expiration)
                    print(values)
    else:
        # For equities and fx.
        for exchange in exchanges:
            for symbol in symbols[exchange]:
                values = read_ticks_files(root,
                                          exchange=exchange,
                                          symbol=symbol)
                print(values)

    # Print list indexed by [exchange symbol expiry] with
    # [date_collected start_time end_time] for collected data.
    if (group == 'futures'):
        expiry = set_expiry(root, exchanges, symbols)
        for exchange in exchanges:
            for symbol in symbols[exchange]:
                for expiration in expiry[symbol]:
                    label = [exchange, symbol, expiration]
                    values = get_tks_datetime(root,
                                              exchange=exchange,
                                              symbol=symbol,
                                              expiry=expiration)
                    print label, values
    else:
        # For equities and fx.
        for exchange in exchanges:
            for symbol in symbols[exchange]:
                label = [exchange, symbol]
                values = get_tks_datetime(root,
                                          exchange=exchange,
                                          symbol=symbol)
                print label, values

    # Print list containing lines of full path to ticks files
    # containing duplicate entries.
    if (group == 'futures'):
        expiry = set_expiry(root, exchanges, symbols)
        for exchange in exchanges:
            for symbol in symbols[exchange]:
                for expiration in expiry[symbol]:
                    values = find_duplicates(root,
                                             exchange=exchange,
                                             symbol=symbol,
                                             expiry=expiration)
                    print(values)
    else:
        # For equities and fx.
        for exchange in exchanges:
            for symbol in symbols[exchange]:
                values = find_duplicates(root,
                                         exchange=exchange,
                                         symbol=symbol)
                print(values)


if __name__ == '__main__':
    main()
