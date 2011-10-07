"""
Statistical functions for determining good predictors.

"""

import math
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

__author__ = "Todd Minehardt"
__copyright__ = "Copyright 2011, bicycle trading, llc"
__maintainer__ = "Todd Minehardt"
__email__ = "todd@bicycletrading.com"

def gcd(a, b):
    """Return greatest common divisor."""
    while b:
        a, b = b, a % b
    return a

def ks_signif(x):
    """
    Return smallest significance level for rejecting null hypothesis,
    using the asymptotic limiting case to compute Q(x) for x > 0.

    """
    if (x <= 0.0):
        return 0.0
    y = 0.0
    for i in range(-20, 20):
        y += math.pow(-1.0, i) * math.exp(-2.0 * i**2 * x**2)
    return (1.0 - y)

def lift(x, y, buy_threshold=0.0, sell_threshold=0.0, plot=True):
    """
    Construct lift curves and summary statistics for buy and sell targets.

    """
    if (len(x) != len(y)):
        return 0

    # stack predictor and target vectors
    data = np.column_stack((x, y))

    # number of observations = # of rows of data
    nobv = data.shape[0]

    # sort data on predictor (column 0), high to low
    idx = data[:, 0].argsort()[::-1]
    data = data[idx]

    # lift for buy and sell targets
    liftBuy = np.where(data[:, 1] > 
                          buy_threshold, 1.0, 0.0).cumsum()
    liftSell = np.where(data[:, 1][::-1] < 
                           sell_threshold, -1.0, 0.0).cumsum()

    # mean lift = (total # of targets in class buy or sell) / nobv
    #meanLiftBuy =  liftBuy[-1] / float(nobv)
    #meanLiftSell = liftSell[-1] / float(nobv)

    # output [column]:
    # [0] buy or sell
    # [1] percent of ordered observations
    # [2] raw lift
    # [3] ratio of lift to mean lift for the percentile
    # [4] number of samples in the percentile

    bins = np.floor(np.sqrt(nobv) + 0.5).astype(int)
    step = nobv / bins
    idx = [np.floor(float(i) / nobv * 100.0 + 0.5) for i in
            range(1, nobv+1)]

    # zero-pad element 0 of rawLift arrays
    rawLiftBuy = np.insert(
        (np.array([liftBuy[i] / float(i) for i in range(1, nobv)])),
        0, 0.0)
    rawLiftSell = np.insert(
        (np.array([liftSell[i] / float(i) for i in range(1, nobv)])),
        0, 0.0)

    print 'buy:'
    for i in range(step-1, nobv, step):
        print '{0:.2f} {1:.3f} {2:.3f} {3:3d}'.format(
            idx[i],
            rawLiftBuy[i],
            100.0 *
            (((rawLiftBuy[i] * float(nobv)) / liftBuy[-1]) - 1.0) /
            idx[i],
            i)

    print
    
    print 'sell:'
    for i in range(step-1, nobv, step):
        print '{0:.2f} {1:.3f} {2:.3f} {3:3d}'.format(
            idx[i],
            rawLiftSell[i],
            100.0 *
            (((rawLiftSell[i] * float(nobv)) / liftSell[-1]) - 1.0) /
            idx[i],
            i)

    # normalize lift by subtracting the cumulative mean lift
    liftBuy -= np.array([liftBuy[-1] / float(nobv)] * nobv).cumsum()
    liftSell -= np.array([liftSell[-1] / float(nobv)] * nobv).cumsum()

    if (plot == True):
        plot_lift(liftBuy, data[:, 0], liftSell, data[:, 0][::-1])
    return

def ks(x, y, plot=True):
    """
    Kolmogorov-Smirnov two-sided, two-sample test.

    Returns tuple of the test statistic for arrays `x` and `y` and
    the significance level for rejecting the null hypothesis.
    The empirical distribution functions F(t) and G(t) are
    computed and (optionally) plotted.

    """
    if (len(x) == 0 or len(y) == 0):
        return 0
    # m, n = # of rows in each array x, y
    m = x.shape[0]
    n = y.shape[0]

    # compute GCD for (m, n)
    d = float(gcd(m, n))

    # flatten, concatenate and sort all data from low to high
    Z = np.concatenate((x.flatten(), y.flatten()))
    Z = np.sort(Z)

    # ECDFs evaluated at ordered combined sample values Z
    F = np.zeros(len(Z))
    G = np.zeros(len(Z))

    # compute J
    J = 0.0
    for i in range(len(Z)):
        for j in range(m):
            if (x[j] <= Z[i]):
                F[i] += 1
        F[i] /= float(m)
        for j in range(n):
            if (y[j] <= Z[i]):
                G[i] += 1
        G[i] /= float(n)
        J_max = np.abs(F[i] - G[i])
        J = max(J, J_max)
    J *= m * n / d
    # the large-sample approximation
    J_star = J * d / np.sqrt(m * n * (m + n))

    if (plot == True):
        y = np.arange(m + n) / float(m + n)
        plt.plot(F, y, 'm-', label='F(t)')
        plt.plot(G, y, 'b-', label='G(t)')
        plt.xlabel('value')
        plt.ylabel('cumulative probability')
        mpl.rcParams['legend.loc'] = 'best'
        plt.legend()
        plt.text(0.05, 0.05,
                 'Copyright 2011 bicycle trading, llc',
                 fontsize=15, color='gray', alpha=0.6)
        plt.show()
    return '{0:.4f} {1:.4f}'.format(J_star, ks_signif(J_star))

def plot_lift(y1, y2, y3, y4):
    """Plot normalized lift and sorted predictors."""
    n = len(y1)
    fig = plt.figure()
    p1 = fig.add_subplot(111)
    x = np.arange(n)
    p1.plot(x, y1, 'b-')
    p1.grid(which='both')
    p1.minorticks_on()
    p1.set_xlabel('observations')
    p1.set_ylabel('normalized lift - buy', color='b')
    for tick in p1.get_yticklabels():
        tick.set_color('b')
    p2 = p1.twinx()
    p2.plot(y2, 'b-')
    p3 = p1.twinx()
    p3.plot(y3, 'r-')
    p3.set_ylabel('normalized lift - sell', color='r')
    for tick in p3.get_yticklabels():
        tick.set_color('r')
    p4 = p1.twinx()
    p4.plot(y4, 'r-')
    yticklabels = p2.get_yticklabels() + p4.get_yticklabels()
    yticklines = p2.get_yticklines() + p4.get_yticklines()
    plt.setp(yticklabels, visible=False)
    plt.setp(yticklines, visible=False)
#    plt.show()
    return

def roc(x, y, theta=0.0, plot=True):
    """
    ROC curve plot and statistics.

    """
    if (len(x) == 0 or len(y) == 0):
        return 0
    # total # of positives and negatives in target
    P = np.where(y >= theta, 1.0, 0.0).sum()
    N = np.where(y < theta, 1.0, 0.0).sum()

    # true P, false P rates
    TPR = np.logical_and(np.where(x >= theta, 1.0, 0.0),
                            np.where(y > 0.0, 1.0, 0.0)).astype(float)
    FPR = np.logical_and(np.where(x >= theta, 1.0, 0.0),
                            np.where(y < 0.0, 1.0, 0.0)).astype(float)
    
    # TP, FP, FN, TN
    TP = TPR.sum()
    FP = FPR.sum()
    FN = P - TP
    TN = N - FP

    # report as fractions
    TPF = TP / (TP + FN)
    FPF = FP / N
    FNF = 1 - TPF
    TNF = TN / (TN + FP)
    
    # diagnostic likelihood ratios
    DLRP = TPF / FPF
    DLRN = FNF / TNF

    # probability of a positive predictor
    tau = (TP + FP) / (P + N)

    # probability of a positive target
    rho = (TP + FN) / (P + N)

    # positive predictive value
    PPV = TP / (TP + FP)

    # negative predictive value
    NPV = TN / (TN + FN)

    print 'threshold: {0:.4f}'.format(theta)
    print
    print 'Classification probabilities on [0, 1]'
    print 'FPF: {0:.3f} TPF: {1:.3f} tau: {2:.3f}'.format(FPF, TPF, tau)
    print
    print 'Predictive values on [0, 1]'
    print 'PPV: {0:.3f} NPV: {0:.3f} rho: {2:.3f}'.format(PPV, NPV, rho)
    print
    print 'Diagnostic likelihood ratios on [0, +oo)'
    print 'DLR+: {0:.3f} DLR-: {1:.3f}'.format(DLRP, DLRN)

    if (plot == True):
        pass
    
    return

