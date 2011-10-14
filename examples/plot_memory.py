"""
Plot memory usage of a numeric computation using numpy and scipy
"""
import numpy as np
from minimon import memory
from scipy import linalg

X = np.random.randn(1000, 1000)
y = np.random.randn(1000)
mm = memory("linalg.qr_multiply(X, y)", interval=.01, locals=locals())
mm2 = memory("R, Q = linalg.qr(X);np.dot(Q.T, y)", interval=.01, locals=locals())
mm1 = (np.array(mm) * 4.) / 1024
mm2 = (np.array(mm2) * 4.) / 1024
mm1.resize(mm2.shape)

import pylab as pl
x = np.linspace(0, np.max(mm1), len(mm1))
pl.plot(x, mm1, x, mm2, '+', color='black')
pl.fill_between(x, mm1, alpha=0.2, dashes='dotted', linewidth=.1, label='with qr_multiply')
pl.fill_between(x, mm2, alpha=0.2, color='yellow', label='naive computation')
pl.legend()
pl.show()
