from memory_profiler import profile

@profile
def func_1(i):
    # .. will be called twice ..
    c = {}
    for i in range(i):
        c[i] = 2

def test_func():

    func_1(10)
    func_1(10000)
