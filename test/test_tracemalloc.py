from io import StringIO
from time import sleep

from memory_profiler import profile

try:
    import tracemalloc
    has_tracemalloc = True
except ImportError:
    has_tracemalloc = False

output = StringIO()

# allowable error in MB
EPSILON = 0.0001


def test_memory_profiler(test_input, expected):
    mem_prof(test_input)
    inc, dec = parse_mem_prof()
    assert abs(inc - dec) <= EPSILON, \
        'inc = {}, dec = {}, err = {}'.format(inc, dec, abs(inc - dec))
    assert abs(inc - expected) <= EPSILON, \
        'inc = {}, size = {}, err = {}'.format(
            inc, expected, abs(inc - expected)
        )


@profile(stream=output, precision=6, backend='tracemalloc')
def mem_prof(n):
    a = bytearray(n)
    del a
    sleep(1)


def parse_mem_prof():
    text = output.getvalue().split('\n')

    def f(s):
        return float(s.split()[3])

    return f(text[-6]), -f(text[-5])

if __name__ == '__main__':
    if has_tracemalloc:
        tests = [
            (100, 0.00012302398681640625),
            (1000, 0.0009813308715820312),
            (10000, 0.009564399719238281),
            (100000, 0.09539508819580078),
            (1000000, 0.9537019729614258),
            (10000000, 9.536770820617676),
            (100000000, 95.36745929718018),
        ]
        for test_input, expected in tests:
            test_memory_profiler(test_input, expected)
