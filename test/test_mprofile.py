"""This script is intended as a test case for mprofile"""

import time

@profile
def test1(l):
    a = [1] * l
    time.sleep(1)
    return a

@profile
def test2(l):
    b = [1] * l
    time.sleep(1)
    return b

if __name__ == "__main__":
    l = 100000
    test1(l)
    test2(2 * l)

