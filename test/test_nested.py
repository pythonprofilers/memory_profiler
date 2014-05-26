# .. an example with a for loop ..

import time

@profile
def test_1():
    a = [1] * (10 ** 6)
    b = [2] * (2 * 10 ** 7)
    del b

    def test_2():
        a = [1] * (10 ** 6)
        b = [2] * (2 * 10 ** 7)
        del b

        return a

    return test_2


if __name__ == '__main__':
    profile.enable_by_count()

    test_2 = test_1()
    time.sleep(1)
    test_2()
    time.sleep(1)

    profile.disable_by_count()
