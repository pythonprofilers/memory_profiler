import pytest
import tracemalloc
from io import StringIO
from time import sleep

from memory_profiler import profile
import memory_profiler

tracemalloc.start()
output = StringIO()

# allowable error in MB
EPSILON = 0.0001

memory_profiler._backend = 'tracemalloc'


@pytest.mark.parametrize('test_input,expected', [
    (100, 0.00012302398681640625),
    (1000, 0.0009813308715820312),
    (10000, 0.009564399719238281),
    (100000, 0.09539508819580078),
    (1000000, 0.9537019729614258),
    (10000000, 9.536770820617676),
    (100000000, 95.36745929718018),
])
def test_memory_profiler(test_input, expected):
    mem_prof(test_input)
    inc, dec = parse_mem_prof()
    assert abs(inc - dec) <= EPSILON, 'inc = {}, dec = {}, err = {}'.format(inc, dec, abs(inc - dec))
    assert abs(inc - expected) <= EPSILON, 'inc = {}, size = {}, err = {}'.format(inc, expected, abs(inc - expected))


@profile(stream=output, precision=6)
def mem_prof(n):
    a = bytearray(n)
    del a
    sleep(1)


def parse_mem_prof():
    text = output.getvalue().split('\n')

    def f(s):
        return float(s.split()[3])

    return f(text[-6]), -f(text[-5])
