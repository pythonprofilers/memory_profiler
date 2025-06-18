"""This script is intended as a test case for mprofile"""

import time

from memory_profiler import profile


@profile
def func1(l):
    """func1 docstring"""
    a = [1] * l
    time.sleep(1)
    return a

@profile
def func2(l):
    b = [1] * l
    time.sleep(1)
    return b

def func3(l):
    """func3 docstring"""
    return l

def test_mprofile():
    l = 100000
    func1(l)
    func2(2 * l)

    # make sure that the function name and docstring are set
    # by functools.wraps
    # memory_profile.py def profile func is not None case
    assert (func1.__name__ == 'func1'), 'function name is incorrect'
    assert (func1.__doc__ == 'func1 docstring'), 'function docstring is incorrect'
    # memory_profile.py def profile func is None case
    profile_maker = profile()
    profiled_test3 = profile_maker(func3)
    assert (profiled_test3.__name__ == 'func3'), 'function name is incorrect'
    assert (profiled_test3.__doc__ == 'func3 docstring'), 'function docstring is incorrect'
