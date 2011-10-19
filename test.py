"""Run as
    $ python minimon.py test.py
"""

@profile
def sample():
    a = 2
    a + 3
    a = [0] * 3000000
    del a
    b = 2

    2 + 3

sample()
