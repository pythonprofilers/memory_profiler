import sys


PY2 = sys.version_info[0] == 2

try:
    import tracemalloc  # noqa
except ImportError:
    HAS_TRACEMALLOC = False
else:
    HAS_TRACEMALLOC = True

TWO_20 = float(2 ** 20)
