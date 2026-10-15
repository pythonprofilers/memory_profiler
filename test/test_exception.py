
# make sure that memory profiler does not hang on exception
from memory_profiler import memory_usage

def foo():
    raise NotImplementedError('Error')

if __name__ == '__main__':
    try:
        out = memory_usage((foo, tuple(), {}), timeout=1)
    except NotImplementedError:
        pass
    print('Success')
