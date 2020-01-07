import sys


PY2 = sys.version_info[0] == 2

PY34 = (3, 4) < sys.version_info

try:
    import tracemalloc  # noqa
except ImportError:
    HAS_TRACEMALLOC = False
else:
    HAS_TRACEMALLOC = True

TWO_20 = float(2 ** 20)
