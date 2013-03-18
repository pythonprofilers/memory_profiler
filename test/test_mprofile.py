"""This script is intended as a test case for mprofile"""

import time

@profile
def test1():
    a = [1] * 100000
    time.sleep(1)
    return a

@profile
def test2(l):
    b = [2 * n for n in l]
    time.sleep(1)
    del b


if __name__ == "__main__":
    time.sleep(1)
    l = test1()
    test2(l)
    time.sleep(1)

