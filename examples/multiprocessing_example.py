"""
An undecorated example of a script that allocates memory in multiprocessing
workers to demonstrate the use of memory_profiler with multiple processes.

Run this script with mprof run -M multiprocessing_example.py
You can then visualize the usage with mprof plot.
"""

import time
import multiprocessing as mp

# Big numbers
X6 = 10 ** 6
X7 = 10 ** 7


def worker(num, wait, amt=X6):
    """
    A function that allocates memory over time.
    """
    frame = []

    for idx in range(num):
        frame.extend([1] * amt)
        time.sleep(wait)

    del frame


def main_sequential():
    """
    A sequential version of the work, where one worker is called at a time.
    """
    worker(5, 5, X6)
    worker(5, 2, X7)
    worker(5, 5, X6)
    worker(5, 2, X7)


def main_multiproc():
    """
    A multiprocessing version of the work, where workers work in their own
    child processes and are collected by the master process.
    """
    pool    = mp.Pool(processes=4)
    tasks   = [
        pool.apply_async(worker, args) for args in
        [(5, 5, X6), (5, 2, X7), (5, 5, X6), (5, 2, X7)]
    ]

    results = [p.get() for p in tasks]


if __name__ == '__main__':
    main_multiproc()
