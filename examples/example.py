import numpy as np

@profile
def my_func():
    a = np.zeros((100, 100))
    b = np.zeros((1000, 1000))
    c = np.zeros((10000, 1000))
    return a, b, c

if __name__ == '__main__':
    my_func()
