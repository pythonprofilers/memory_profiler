from memory_profiler import profile

f=open('hi.txt','w+')

@profile(stream=f)
def my_func():
    a = [1] * (10 ** 6)
    b = [2] * (2 * 10 ** 7)
    del b
    return a

@profile(stream=f)
def my_func1():
    a = [2] * (10 ** 6)
    b = [3] * (2 * 10 ** 7)
    del b
    return a

if __name__ == '__main__':
    my_func()
    my_func1()