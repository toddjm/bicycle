#!/usr/bin/env python
"""Read tks files in text/numpy record format, write in text."""

import argparse
import collections
import datetime
import numpy
import os

__author__ = "Todd Minehardt"
__copyright__ = "Copyright 2011, 2012 bicycle trading, llc"
__email__ = "todd@bicycletrading.com"


def read_tks_file(filename):
    """Read tks file."""
    values = []
    with open(filename, 'r') as infile:
        values = infile.readlines()    
    values = [i.strip() for i in values]
    values = [i.split() for i in values]
    for i in values:
        line = str(float(i[0])), str(float(i[1])), str(float(i[2])),
               str(float(i[3])), str(float(i[4])), str(int(float(i[5]))),
               str(int(float(i[6]))), str(float(i[7])),
               str(int(float(i[8])))
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


def set_parser():
    """Return parser for command line arguments."""
    values = argparse.ArgumentParser(description='Read/write tks files.')
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
    return values


def write_tks_file(filename, data):
    """Write tks file."""
    # Save original.
    with open(filename + '.original', 'w') as outfile:
        outfile.write(data)
    # Overwrite tks file.
    with open(filename, 'w') as outfile:
        for line in data:
            ts = line.split()[0] 
            op = float(line.split()[2])
            hi = float(line.split()[3])
            lo = float(line.split()[4])
            cl = float(line.split()[5])
            vl = line.split()[6]
            vw = float(line.split()[7])
            gp = line.split()[8]
            ct = line.split()[9]
            print('{0} {1} {2} {3} {4} {5} {6} {7} {8}').format(
              ts, op, hi, lo, cl, vw, ct, vw, gp)
    return


def main():
    """Read tks file, write tks files. """
    # Parse command line arguments, set local variables.
    parser = set_parser()
    exchanges = parser.parse_args().exchanges
    group = parser.parse_args().group
    source = parser.parse_args().source

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
