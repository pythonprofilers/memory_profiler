
@profile
def test_1():
    # .. will be called twice ..
    c = {}
    for i in range(1000):
        c[i] = 2

from memory_profiler import LineProfiler as MemeryProfiler, show_results
mp = MemeryProfiler(enable_global=True)
@mp
def test_inner_func():
    c = dict((i, i*2) for i in xrange(10000))
    
    def inner_func():
        inner_c = [1] * 1024 * 1024 * 5
        return inner_c
    
    del c
    inner_func()

    import os
    dirs = list(os.walk("."))


if __name__ == '__main__':
    test_1()
    test_1()

    test_inner_func()
    show_results(mp)
