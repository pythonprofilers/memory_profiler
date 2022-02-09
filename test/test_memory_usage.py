from memory_profiler import memory_usage
import os


def some_func(*args, **kwargs):
    return args, kwargs


def test_memory_usage():
    # Check that memory_usage works with functions with star args.
    mem, ret = memory_usage((some_func, (1, 2), dict(a=1)), retval=True)
    assert ret[0] == (1, 2)
    assert ret[1] == dict(a=1)
    
    
def write_line(filepath):
    with open(filepath, 'a') as the_file:
        the_file.write('Testing\n')

def test_max_iterations():
    # Check that memory_usage works with max_iterations set (for python functions).
    this_dir = os.path.dirname(os.path.realpath(__file__))
    file = os.path.join(this_dir, 'temp_test_max_iterations_file.txt')
    mem = memory_usage((write_line, (file, ), dict()), max_usage=True, max_iterations=1)
    n_lines = sum(1 for line in open(file))
    os.remove(file)
    assert n_lines == 1


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
    test_max_iterations()
    test_return_value_consistency()
