# .. an example with a for loop ..

import time

from memory_profiler import profile


@profile
def func_1():
    a = [1] * (10 ** 6)
    b = [2] * (2 * 10 ** 7)
    time.sleep(0.6)
    del b

    for i in range(2):
        a = [1] * (10 ** 6)
        b = [2] * (2 * 10 ** 7)
        del b
    return a

@profile
def func_2():
    a = {}
    time.sleep(0.5)
    for i in range(10000):
        a[i] = i + 1
    time.sleep(0.6)
    return

def test_loop_decorated():
    func_1()
    func_2()
