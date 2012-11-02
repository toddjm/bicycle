"""
Signal types.

"""

from collections import deque
import numpy as np

__author__ = "Todd Minehardt"
__copyright__ = "Copyright 2011, bicycle trading, llc"
__email__ = "todd@bicycletrading.com"


def ema(data, alpha):
    """
    Returns exponential moving average of data, smoothing constant alpha.

    >>> print ema([1, 2, 3, 4, 5], 1.0/3.0)
    [ 1.          1.33333333  1.88888889  2.59259259  3.39506173]

    """
    if len(data) == 0:
        return 0
    values = np.zeros(len(data))
    values[0] = data[0]
    for i in range(1, len(data)):
        values[i] = alpha * data[i] + (1.0 - alpha) * values[i - 1]
    return values


def dema(data, alpha, delta):
    """
    Returns the change in the EMA of data, smoothing constant alpha,
    differenced by delta time steps.

    """
    if len(data) == 0:
        return 0
    ema_data = ema(data, alpha)
    len_data = len(data)
    return (ema_data[len_data] - ema_data[len_data - delta])


def rofc(data, periods):
    """
    Returns the `periods`-period rate of change indicator.

    """
    if len(data) == 0:
        return 0
    values = [0.0] * periods
    temp = 0.0
    for i in range(periods, len(data)):
        temp = 100.0 * ((data[i] - data[i - periods]) / data[i - periods])
        values.append(temp)
    return np.array(values)


def rsi(data, periods):
    """
    Returns the `periods`-period Relative Strength Index (RSI).
    """
    if len(data) == 0:
        return 0
    avg_gain = 0.0
    avg_loss = 0.0
    values = [0.0] * periods
    cnt = 0.0
    for i in range(1, periods + 1):
        cnt = data[i] - data[i - 1]
        if (cnt > 0.0):
            avg_gain += cnt
        elif (cnt < 0.0):
            avg_loss += abs(cnt)
    avg_gain /= float(periods)
    avg_loss /= float(periods)
    values.append(avg_gain / avg_loss)
    for i in range(periods + 1, len(data)):
        cnt = data[i] - data[i - 1]
        if (cnt > 0.0):
            avg_gain = (avg_gain * (periods - 1) + cnt) / float(periods)
            avg_loss *= (periods - 1) / float(periods)
        elif (cnt < 0.0):
            avg_gain *= (periods - 1) / float(periods)
            avg_loss = (avg_loss * (periods - 1) + abs(cnt)) / float(periods)
        values.append(avg_gain / avg_loss)
    for i in range(len(values)):
        values[i] = 100.0 - (100.0 / (1.0 + values[i]))
    return np.array(values)


def dpo(data, periods):
    """
    Returns the `periods`-period detrended price oscillator.

    """
    if len(data) == 0:
        return 0
    cnt = 1
    p_small = (periods / 2) + 1
    values = [data[periods - p_small] - data[0]]
    sma_data = sma(data, periods)
    for i in range(periods, len(data)):
        values.append(data[i - p_small] - sma_data[cnt])
        cnt += 1
    return np.array(values)


def sma(data, periods):
    """
    Returns the `periods`-period simple moving average.

    """
    if len(data) == 0:
        return 0
    d_value = 0.0
    temp = deque([0.0] * periods)
    total = 0.0
    values = []
    for i in range(len(data)):
        temp.append(data[i])
        total += data[i] - temp.popleft()
        d_value = min(d_value + 1, periods)
        values.append(total / d_value)
    return np.array(values)


def cma(data):
    """
    Returns cumulative moving average of data.

    >>> print cma([10, 20, 30, 40, 50])
    [ 10.  15.  20.  25.  30.]

    """
    if len(data) == 0:
        return 0
    values = []
    temp = 0.0
    for i in range(len(data)):
        temp = (data[i] + (i * temp)) / (i + 1.0)
        values.append(temp)
    return np.array(values)


def zscore(data):
    """Returns new array of z-scores.

    """
    if len(data) == 0:
        return 0
    return ((data - np.mean(data)) / np.std(data))


def normalize(data):
    """Returns new array of data with values mapped to [-1,1].

    """
    if len(data) == 0:
        return 0
    return (2.0 * (data - np.min(data)) / (np.max(data) - np.min(data))) - 1.0


def argfind(bool_signal):
    """xxx"""
    return np.nonzero(bool_signal)[0]


def argcnt(bool_signal):
    """xxx"""
    return len(argfind(bool_signal))


def argtake(signal, bool_signal):
    """xxx"""
    return np.take(signal, argfind(bool_signal))


def lshift(signal, steps=1):
    """
    Return new array of `signal` shifted to the left by `steps`
    filling the end of the array with the last value in `signal`
    to preserve the original length.

    """
    return np.append(np.delete(signal, slice(0, steps)),
                     np.repeat(signal[-1], steps))


def rshift(signal, steps=1, init=None):
    """
    Return new array of `signal` shifted to the right by `steps`
    filling the beginning of the array with the first value in
    `signal` (or the value of `init`) to preserve the original length.

    """
#    init = signal[0] if init == None else init
    if init is None:
        init = signal[0]
    return np.resize(np.insert(np.copy(signal), np.zeros(steps),
                               [init]), len(signal))
