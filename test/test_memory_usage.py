from memory_profiler import memory_usage


def some_func(*args, **kwargs):
    return args, kwargs


def test_memory_usage():
    # Check that memory_usage works with functions with star args.
    mem, ret = memory_usage((some_func, (1, 2), dict(a=1)), retval=True)
    assert ret[0] == (1, 2)
    assert ret[1] == dict(a=1)

if __name__ == "__main__":
    test_memory_usage()
