# coding: utf-8

import time

@profile
def test_unicode():
    # test when unicode is present
    exec("β = 0")
    return

if __name__ == '__main__':
    # run only for Python 3
    import sys
    if sys.version_info >= (3, 0):
        test_unicode()
