# .. an example with a for loop ..


@profile
def my_func():
    a = {}
    for i in range(10000):
        a[i] =  i + 1
    return

if __name__ == '__main__':
    my_func()
