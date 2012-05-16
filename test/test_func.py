
@profile
def test_1():
    # .. will be called twice ..
    c = {}
    for i in range(1000):
        c[i] = 2

if __name__ == '__main__':
    test_1()
    test_1()
