import math
from memory_profiler import profile

@profile
def f():
    o = math.sqrt(2013)
    return o

def test_f():
    f()
