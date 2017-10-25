from memory_profiler import profile


def gen(count):
    r = list(range(0,count))
    return r

_global_var = []
def _gen_cache():
    global _global_var
    if not _global_var:
        _global_var = gen(1000000)

@profile(precision=4)
def test():
    a = gen(90000)
    for i in range(0,3):
        b = i
        def _inner_gen():
            gen(1024*1024*20)
        h = i
        _gen_cache()
        _inner_gen()
        g = i

if __name__ == "__main__":
    test()
