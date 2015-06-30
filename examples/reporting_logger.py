from memory_profiler import profile
import logging

# create logger
logger = logging.getLogger('memory_profile_log')
logger.setLevel(logging.DEBUG)

# create file handler which logs even debug messages
fh = logging.FileHandler("memory_profile.log")
fh.setLevel(logging.DEBUG)

# create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)

# add the handlers to the logger
logger.addHandler(fh)

from memory_profiler import LogFile
import sys
sys.stdout = LogFile('memory_profile_log', reportIncrementFlag=False)

@profile
def my_func():
    a = [1] * (10 ** 6)
    b = [2] * (2 * 10 ** 7)
    del b
    return a

@profile
def my_func1():
    a = [2] * (10 ** 6)
    b = [3] * (2 * 10 ** 7)
    del b
    return a

if __name__ == '__main__':
    my_func()
    my_func1()
