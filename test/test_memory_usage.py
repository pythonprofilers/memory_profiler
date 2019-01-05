from memory_profiler import memory_usage


def some_func(*args, **kwargs):
    return args, kwargs


def test_memory_usage():
    # Check that memory_usage works with functions with star args.
    mem, ret = memory_usage((some_func, (1, 2), dict(a=1)), retval=True)
    assert ret[0] == (1, 2)
    assert ret[1] == dict(a=1)


def test_return_value_consistency():
    # Test return values when watching process by PID
    pid_mem_list = memory_usage(timeout=1)
    assert type(pid_mem_list) == list, "Memory usage of process should be a list"
    pid_mem_max = memory_usage(timeout=1, max_usage=True)
    assert type(pid_mem_max) == float, "Max memory usage of process should be a number"
    # Test return values when watching callable
    func_mem_list = memory_usage((some_func, (42,), dict(a=42)))
    assert type(func_mem_list) == list, "Memory usage of callable should be a list"
    func_mem_max = memory_usage((some_func, (42,), dict(a=42)), max_usage=True)
    assert type(func_mem_max) == float, "Max memory usage of callable should be a number"


if __name__ == "__main__":
    test_memory_usage()
    test_return_value_consistency()
