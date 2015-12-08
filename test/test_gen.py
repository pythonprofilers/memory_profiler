
@profile
def my_func():
    a = [1] * (10 ** 6)
    b = [2] * (2 * 10 ** 7)
    del b
    yield a


@profile
def test_comprehension():
    # Dict comprehension
    d_comp = {str(k*k): [v] * (1<<17)
              for (v, k) in enumerate(range(99, 111))}

    # List comprehension
    l_comp = [[i] * (i<<9) for i in range(99)]
    del l_comp
    del d_comp

    def hh(x=1):
        # Set comprehension
        s_comp = {('Z',) * (k<<13) for k in range(x, 19 + 2*x)}
        return s_comp

    val = [range(1, 4), max(1, 4), 42 + len(hh())]
    val = hh() | hh(4)
    val.add(40)
    l1_comp = [[(1, i)] * (i<<9) for i in range(99)]
    l2_comp = [[(3, i)] * (i<<9) for i in range(99)]

    return val


@profile
def test_generator():
    a_gen = ([42] * (1<<20) for __ in '123')
    huge_lst = list(a_gen)

    b_gen = ([24] * (1<<20) for __ in '123')
    del b_gen
    del huge_lst

    return a_gen


if __name__ == '__main__':
    with profile:
        next(my_func())     # Issue #42

    test_generator()
    test_comprehension()
