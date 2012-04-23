#!/usr/bin/env python
"""Read tks files in text/numpy record format, write in text."""

import argparse
import bisect
import collections
import datetime
import numpy
import os

__author__ = "Todd Minehardt"
__copyright__ = "Copyright 2011, 2012 bicycle trading, llc"
__email__ = "todd@bicycletrading.com"


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



def read_tks_file(filename):
    """Read tks file."""
    values = []
    with open(filename, 'r') as infile:
        values = infile.readlines()    
    values = [i.strip() for i in values]
    for i in values:
        i[0] = str(float(i.split()[0]))
        i[1] = str(float(i.split()[1]))
        i[2] = str(float(i.split()[2]))
        i[3] = str(float(i.split()[3]))
        i[4] = str(float(i.split()[4]))
        i[5] = str(int(i.split()[5]))
        i[6] = str(int(i.split()[6]))
        i[7] = str(float(i.split()[7]))
        i[8] = str(int(i.split()[8]))
    return values

    for i in range(len(xxx)):
        for j in range(len(xxx[i])):
        print xxx[i][j], type(xxx[i][j])

    return values


def write_tks_file(filename, data):
    """Write tks file."""
    savefile = filename + '.original'
    



        for line in tks:
            timestamp = line.split()[0] 
            open_price = float(line.split()[2])
            high_price = float(line.split()[3])
            low_price = float(line.split()[4])
            close_price = float(line.split()[5])
            volume = line.split()[6]
            vwap = float(line.split()[7])
            gaps = line.split()[8]
            count = line.split()[9]
            print('{0} {1} {2} {3} {4} {5} {6} {7} {8}').format(
              timestamp,
              open_price,
              high_price,
              low_price,
              close_price,
              volume,
              count,
              vwap,
              gaps)

if __name__ == '__main__':
    main()
    

 
    recordtype = ([('timestamp', float), ('open', float), ('high', float),
                   ('low', float), ('close', float), ('volume', int),
                   ('orders', int), ('vwap', float), ('gaps', bool)])
                if (os.path.isfile(infile) and os.stat(infile).st_size != 0):
                    timestamps = []
                    if tks.ndim != 0:
                        timestamps = [tks[i][0] for i in range(len(tks))]
                        timestamps.sort()
                        counter = collections.Counter(timestamps)
                        if bool([i for i in counter.values() if i > 1]):
                            tks = numpy.loadtxt(infile, dtype=recordtype)



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
