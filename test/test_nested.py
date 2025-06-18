# .. an example with a for loop ..


from memory_profiler import LineProfiler


def func_1():
    a = [1] * (10 ** 6)
    b = [2] * (2 * 10 ** 7)
    del b

    def func_2():
        a = [1] * (10 ** 6)
        b = [2] * (2 * 10 ** 7)
        del b

        return a

    return func_2


def test_nested():
    profiler = LineProfiler()
    profiler.enable_by_count()
    wrapped = profiler(func_1)
    wrapped()
    profiler.disable_by_count()
