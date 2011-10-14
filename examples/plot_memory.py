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
p = pl.fill_between(x, mm1)
p.set_facecolors('none')
ax = pl.axes()
from matplotlib.patches import PathPatch
for path in p.get_paths():
    p1 = PathPatch(path, color='green', fc="none", hatch="//")
    ax.add_patch(p1)
    p1.set_zorder(p.get_zorder() - 0.1)

p = pl.fill_between(x, mm2)
p.set_facecolors('none')
ax = pl.axes()
from matplotlib.patches import PathPatch
for path in p.get_paths():
    p2 = PathPatch(path, color='red', fc="none", hatch="/")
    ax.add_patch(p2)
    p2.set_zorder(p.get_zorder() - .1)
pl.legend([p2, p1], ["naive computation", "qr_multiply"])
pl.xlabel('time')
pl.ylabel('Memory consumption (in MB)')
pl.show()
