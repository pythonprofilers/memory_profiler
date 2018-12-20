"""This script is intended as a test case for mprofile"""

import time

@profile
def test1(l):
    """test1 docstring"""
    a = [1] * l
    time.sleep(1)
    return a

@profile
def test2(l):
    b = [1] * l
    time.sleep(1)
    return b

def test3(l):
    """test3 docstring"""
    return l

if __name__ == "__main__":
    l = 100000
    test1(l)
    test2(2 * l)

    # make sure that the function name and docstring are set
    # by functools.wraps
    # memory_profile.py def profile func is not None case
    assert (test1.__name__ == 'test1'), 'function name is incorrect'
    assert (test1.__doc__ == 'test1 docstring'), 'function docstring is incorrect'
    # memory_profile.py def profile func is None case
    profile_maker = profile()
    profiled_test3 = profile_maker(test3)
    assert (profiled_test3.__name__ == 'test3'), 'function name is incorrect'
    assert (profiled_test3.__doc__ == 'test3 docstring'), 'function docstring is incorrect'
