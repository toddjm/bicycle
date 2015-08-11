#!/usr/bin/python
"""
Convert raw ticks to pointer ticks for futures contracts.
Write pointer ticks to files.

"""

import argparse
import calendar
import os
import sys
import time

__author__ = "Todd Minehardt"
__copyright__ = "Copyright 2011, bicycle trading, llc"
__maintainer__ = "Todd Minehardt"
__email__ = "todd@bicycletrading.com"

if os.getenv("TICKS_HOME") is None:
    return 0

parser = argparse.ArgumentParser(description='Create rolling futures ticks files.')
