
@profile
def test_1():
    # .. will be called twice ..
    a = 2.
    b = 3
    c = {}
    for i in range(1000):
        c[i] = 2
    c[0] = 2.

if __name__ == '__main__':
    test_1()
    test_1()
