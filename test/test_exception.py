import pytest

# make sure that memory profiler does not hang on exception
from memory_profiler import memory_usage

def foo():
    raise NotImplementedError('Error')

def test_hang_on_exception():

    with pytest.raises(NotImplementedError):
        out = memory_usage((foo, tuple(), {}), timeout=1)
