
@profile
def test_1(i):
    # .. will be called twice ..
    c = {}
    for i in range(i):
        c[i] = 2

if __name__ == '__main__':
    test_1(10)
    test_1(10000)
