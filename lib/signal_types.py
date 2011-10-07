"""
Signal types.

"""

from collections import deque
import numpy as np

__author__ = "Todd Minehardt"
__copyright__ = "Copyright 2011, bicycle trading, llc"
__maintainer__ = "Todd Minehardt"
__email__ = "todd@bicycletrading.com"

def ema(x, alpha):
    """
    Returns exponential moving average of x, smoothing constant alpha.

    >>> print ema([1, 2, 3, 4, 5], 1.0/3.0)
    [ 1.          1.33333333  1.88888889  2.59259259  3.39506173]

    """
    if len(x) == 0:
        return 0
    y = np.zeros(len(x))
    y[0] = x[0]
    for i in range(1, len(x)):
        y[i] = alpha * x[i] + (1.0 - alpha) * y[i-1]
    return y

def dema(x, alpha, delta):
    """
    Returns the change in the EMA of x, smoothing constant alpha,
    differenced by delta time steps.

    """
    if len(x) == 0:
       return 0
    y = ema(x, alpha)
    z = len(x)
    return (y[z] - y[z-delta])

def rofc(x, n):
    """
    Returns the `n`-period rate of change indicator.

    """
    if len(x) == 0:
        return 0
    y = [0.0] * n
    z = 0.0
    for i in range(n, len(x)):
        z = 100.0 * ((x[i] - x[i-n]) / x[i-n])
        y.append(z)
    return np.array(y)

def rsi(x, n):
    """
    Returns the `n`-period Relative Strength Index (RSI).
      
    """
    if len(x) == 0:
        return 0
    avg_gain = 0.0
    avg_loss = 0.0
    y = [0.0] * n
    z = 0.0
    for i in range(1, n+1):
        z = x[i] - x[i-1]
        if (z > 0.0):
            avg_gain += z
        elif (z < 0.0):
            avg_loss += abs(z)
    avg_gain /= float(n)
    avg_loss /= float(n)
    y.append(avg_gain / avg_loss)
    for i in range(n+1, len(x)):
        z = x[i] - x[i-1]
        if (z > 0.0):
            avg_gain = (avg_gain * (n - 1) + z) / float(n)
            avg_loss *= (n - 1) / float(n)
        elif (z < 0.0):
            avg_gain *= (n - 1) / float(n)
            avg_loss = (avg_loss * (n - 1) + abs(z)) / float(n)
        y.append(avg_gain / avg_loss)
    for i in range(len(y)):
        y[i] = 100.0 - (100.0 / (1.0 + y[i]))
    return np.array(y)
    
def dpo(x, n):
    """
    Returns the `n`-period detrended price oscillator.

    """
    if len(x) == 0:
        return 0
    cnt = 1
    p = (n / 2) + 1
    y = [x[n-p] - x[0]]
    z = sma(x, n)
    for i in range(n, len(x)):
        y.append(x[i-p] - z[cnt])
        cnt += 1
    return np.array(y)

def sma(x, n):
    """
    Returns the `n`-period simple moving average.

    """
    if len(x) == 0:
        return 0
    d = 0.0
    temp = deque([0.0] * n)
    total = 0.0
    y = list()
    for i in range(len(x)):
        temp.append(x[i])
        total += x[i] - temp.popleft()
        d = min(d+1, n)
        y.append(total / d)
    return np.array(y)

def cma(x):
    """
    Returns cumulative moving average of x.

    >>> print cma([10, 20, 30, 40, 50])
    [ 10.  15.  20.  25.  30.]

    """
    if len(x) == 0:
        return 0
    y = list()
    z = 0.0
    for i in range(len(x)):
        z = (x[i] + (i * z)) / (i + 1.0)
        y.append(z)
    return np.array(y)

def zscore(x):
    """Returns new array of z-scores.

    """
    if len(x) == 0:
        return 0
    return ((x - np.mean(x)) / np.std(x))

def normalize(x):
    """Returns new array of x with values mapped to [-1,1].

    """
    if len(x) == 0:
        return 0
    return (2.0 * (x - np.min(x)) / (np.max(x) - np.min(x))) - 1.0

def argfind(bool_signal):
    return np.nonzero(bool_signal)[0]

def argcnt(bool_signal):
    return len(argfind(bool_signal))

def argtake(signal, bool_signal):
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
    init = signal[0] if init == None else init
    return np.resize(np.insert(np.copy(signal), np.zeros(steps),
                               [init]), len(signal))

