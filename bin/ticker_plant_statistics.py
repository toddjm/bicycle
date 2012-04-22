#!/usr/bin/env python
"""Gather statistics for entries in the ticker plant."""

import argparse
import bisect
import collections
import datetime
import numpy
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
    else:
        return False


def remove_duplicates(root, **kwargs):
    """Remove duplicate rows in tks files, write new file."""
    exchange = kwargs.get('exchange', "")
    expiry = kwargs.get('expiry', "")
    symbol = kwargs.get('symbol', "")
    cwd = os.path.join(root, exchange, symbol, expiry)
    recordtype = ([('timestamp', float), ('open', float), ('high', float),
                   ('low', float), ('close', float), ('volume', int),
                   ('orders', int), ('vwap', float), ('gaps', bool)])
    for year in os.listdir(cwd):
        for month in os.listdir(os.path.join(cwd, year)):
            for day in os.listdir(os.path.join(cwd, year, month)):
                infile = os.path.join(cwd, year, month, day, symbol + '.tks')
                if (os.path.isfile(infile) and os.stat(infile).st_size != 0):
                    tks = numpy.loadtxt(infile, dtype=recordtype)
                    timestamps = []
                    if tks.ndim != 0:
                        timestamps = [tks[i][0] for i in range(len(tks))]
                        timestamps.sort()
                        counter = collections.Counter(timestamps)
                        if bool([i for i in counter.values() if i > 1]):
                            numpy.savetxt(infile + '.original', tks)
                            outlist = []
                            added_keys = set()
                            for i in tks:
                                lookup = tuple(i)[:1]
                                if lookup not in added_keys:
                                    outlist.append(i)
                                    added_keys.add(lookup)
                            outlist = numpy.asarray(outlist, dtype=recordtype)
                            numpy.savetxt(infile, outlist)
    return


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


def get_missing_tks(root, **kwargs):
    """Return list of dates for which there are zero-length tks files."""
    exchange = kwargs.get('exchange', "")
    expiry = kwargs.get('expiry', "")
    symbol = kwargs.get('symbol', "")
    cwd = os.path.join(root, exchange, symbol, expiry)
    dates = []
    for year in os.listdir(cwd):
        for month in os.listdir(os.path.join(cwd, year)):
            for day in os.listdir(os.path.join(cwd, year, month)):
                infile = os.path.join(cwd, year, month, day, symbol + '.tks')
                if (os.path.isfile(infile) and os.stat(infile).st_size == 0):
                    dates.append(year + '/' + month + '/' + day)
    return dates


def get_start_end_datetime(data):
    """Return tuple of start date and time and end time for a data file."""
    start = datetime.datetime.utcfromtimestamp(
             data[0][0]).strftime('%Y/%m/%d %H:%M:%S.%f')
    end = datetime.datetime.utcfromtimestamp(
           data[-1][0]).strftime('%H:%M:%S.%f')
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
    values = [data[i][0] for i in range(len(data))]
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
    recordtype = ([('timestamp', float), ('open', float), ('high', float),
                   ('low', float), ('close', float), ('volume', int),
                   ('orders', int), ('vwap', float), ('gaps', bool)])
    values = []
    for year in os.listdir(cwd):
        for month in os.listdir(os.path.join(cwd, year)):
            for day in os.listdir(os.path.join(cwd, year, month)):
                infile = os.path.join(cwd, year, month, day, symbol + '.tks')
                if (os.path.isfile(infile) and os.stat(infile).st_size != 0):
                    tks = numpy.loadtxt(infile, dtype=recordtype)
                    start, end = get_start_end_datetime(tks)
                    values.append(start + ' ' + end)
    return values


def read_ticks_files(root, **kwargs):
    """Return list of stats for tks files in root dir."""
    exchange = kwargs.get('exchange', "")
    expiry = kwargs.get('expiry', "")
    symbol = kwargs.get('symbol', "")
    cwd = os.path.join(root, exchange, symbol, expiry)
    recordtype = ([('timestamp', float), ('open', float), ('high', float),
                   ('low', float), ('close', float), ('volume', int),
                   ('orders', int), ('vwap', float), ('gaps', bool)])
    values = []
    for year in os.listdir(cwd):
        for month in os.listdir(os.path.join(cwd, year)):
            for day in os.listdir(os.path.join(cwd, year, month)):
                infile = os.path.join(cwd, year, month, day, symbol + '.tks')
                if (os.path.isfile(infile) and os.stat(infile).st_size != 0):
                    tks = numpy.loadtxt(infile, dtype=recordtype)
                    values.append([exchange,
                                   symbol + expiry,
                                   year,
                                   month,
                                   day,
                                   datetime.datetime.utcfromtimestamp(
                                     tks[0][0]).strftime(
                                     '%Y/%m/%d %H:%M:%S.%f'),
                                   datetime.datetime.utcfromtimestamp(
                                     tks[-1][0]).strftime(
                                     '%Y/%m/%d %H:%M:%S.%f'),
                                   len(tks)])
    return values


def set_expiry(root, exchanges, symbols):
    """Return dict for expiry, keyed on symbols."""
    values = {}
    for i in exchanges:
        for j in symbols[i]:
            if os.path.isdir(os.path.join(root, i, j)):
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
    values.add_argument('--exchanges',
                        default=['nymex'],
                        dest='exchanges',
                        help='Space-separated names (default: %(default)s)',
                        nargs='+')
    values.add_argument('--start',
                        default='2011-11-01 00:00:00',
                        dest='start',
                        help='Date string format %%Y-%%m-%%d %%H:%%M:%%S '
                             '(default: %(default)s)')
    values.add_argument('--end',
                        default='2012-01-01 00:00:00',
                        dest='end',
                        help='Date string format %%Y-%%m-%%d %%H:%%M:%%S '
                             '(default: %(default)s)')
    return values


def set_start_end(start, end, data):
    """
    Return tuple of start and end dates modifed if data start
    and/or times are before/after start/end.

    """
    first = datetime.datetime.utcfromtimestamp(data[0][0]).date()
    last = datetime.datetime.utcfromtimestamp(data[-1][0]).date()
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


def show_collected_data(root, exchanges, symbols, **kwargs):
    """Construct dict keyed on exchange with values comprised
    of dicts keyed on symbol[expiry], values collected data dates.

    """
    expiry = kwargs.get('expiry', "")
    for exchange in exchanges:
        for symbol in symbols[exchange]:
            if expiry:
                for expiration in expiry[symbol]:
                    label = [symbol + expiration, exchange]
                    values = get_tks_datetime(root,
                                              exchange=exchange,
                                              symbol=symbol,
                                              expiry=expiration)
                    print label, values
            else:
                label = [symbol, exchange]
                values = get_tks_datetime(root,
                                          exchange=exchange,
                                          symbol=symbol)
                print label, values
    return


def show_information(root, exchanges, symbols, **kwargs):
    """Print list containing lines such as:
    [exchange, symbol [expiry], year_collected, month_collected,
    day_collected, start_time, end_time, number_of_entries]

    """
    expiry = kwargs.get('expiry', "")
    for exchange in exchanges:
        for symbol in symbols[exchange]:
            if expiry:
                for expiration in expiry[symbol]:
                    values = read_ticks_files(root,
                                              exchange=exchange,
                                              symbol=symbol,
                                              expiry=expiration)
                    print(values)
            else:
                values = read_ticks_files(root,
                                          exchange=exchange,
                                          symbol=symbol)
                print(values)
    return


def show_missing_data(root, exchanges, symbols, **kwargs):
    """Construct dict keyed on exchange with values comprised
    of dicts keyed on symbol[expiry], values collected data dates.

    """
    expiry = kwargs.get('expiry', "")
    missing = {}
    for exchange in exchanges:
        for symbol in symbols[exchange]:
            if expiry:
                for expiration in expiry[symbol]:
                    values = get_missing_tks(root,
                                             exchange=exchange,
                                             symbol=symbol,
                                             expiry=expiration)
                    if len(values) != 0:
                        missing[symbol + expiration] = values
            else:
                values = get_missing_tks(root,
                                         exchange=exchange,
                                         symbol=symbol)
                if len(values) != 0:
                    missing[symbol] = values
    return missing


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
            # If tks file does not exist or is zero size,
            # create/append tks file.
            if not os.path.isfile(tks) or os.stat(tks).st_size == 0:
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
    end = parser.parse_args().end
    end = datetime.datetime.strptime(end, '%Y-%m-%d %H:%M:%S')
    exchanges = parser.parse_args().exchanges
    group = parser.parse_args().group
    source = parser.parse_args().source
    start = parser.parse_args().start
    start = datetime.datetime.strptime(start, '%Y-%m-%d %H:%M:%S')

    root = os.path.join(os.getenv('TICKS_HOME'), group, source)
    symbols = set_symbols(root, exchanges)

    if (group == 'futures'):
        expiry = set_expiry(root, exchanges, symbols)

    for exchange in exchanges:
        for symbol in symbols[exchange]:
            if expiry:
                for expiration in expiry[symbol]:
                    remove_duplicates(root,
                                      exchange=exchange,
                                      symbol=symbol,
                                      expiry=expiration)
            else:
                remove_duplicates(root,
                                  exchange=exchange,
                                  symbol=symbol)


if __name__ == '__main__':
    main()
