# .. an example to test decorator with precision keyword argument ..
"""
Test profiling using imported ``profile`` function with precision
specified as parameter to ``profile`` function.
This is useful if the python script we're trying to profile is called as a
module (like `python -m test_module`) and so we can't specify command line
precision parameter.
"""

import time
from memory_profiler import profile

@profile(precision=4)
def test_1():
    a = [1] * (10 ** 6)
    b = [2] * (2 * 10 ** 7)
    time.sleep(0.6)
    del b

    for i in range(2):
        a = [1] * (10 ** 6)
        b = [2] * (2 * 10 ** 7)
        del b
    return a

@profile(precision=5)
def test_2():
    a = {}
    time.sleep(0.5)
    for i in range(10000):
        a[i] = i + 1
    time.sleep(0.6)
    return

if __name__ == '__main__':
    test_1()
    test_2()
