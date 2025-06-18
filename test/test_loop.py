# .. an example with a for loop ..

import time

from memory_profiler import profile


def func_1():
    a = {}
    for i in range(10000):
        a[i] =  i + 1
    return

@profile
def func_2():
    a = [1] * (10 ** 6)
    b = [2] * (2 * 10 ** 7)
    del b

    for i in range(2):
        a = [1] * (10 ** 6)
        b = [2] * (2 * 10 ** 7)
        del b
    return a


def test_loop():
    func_1()
    time.sleep(1)
    func_2()
    time.sleep(1)
