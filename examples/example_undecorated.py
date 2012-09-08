
def another_func():
    """Undecorated function that allocates memory"""
    c = [1] * (10 ** 6)
    d = [1] * (10 ** 7)
    return c, d

if __name__ == '__main__':
    another_func()
