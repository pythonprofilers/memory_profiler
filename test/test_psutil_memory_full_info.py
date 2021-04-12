from memory_profiler import memory_usage

# size = 50000
size = 3000


def test_simple():

    import numpy as np

    def func():
        a = np.random.random((size, size))
        return a

    rss = memory_usage(proc=func, max_usage=True, backend="psutil")
    uss = memory_usage(proc=func, max_usage=True, backend="psutil_uss")
    pss = memory_usage(proc=func, max_usage=True, backend="psutil_pss")
    print(rss, uss, pss)


def test_multiprocessing():

    import numpy as np
    import joblib
    import time

    def func():
        n_jobs = 4
        a = np.random.random((size, size))

        def subprocess(i):
            time.sleep(2)
            return a[i,i]

        results = joblib.Parallel(n_jobs=n_jobs)(
            joblib.delayed(subprocess)(i) 
            for i in range(n_jobs))

        return results

    rss = memory_usage(proc=func, max_usage=True, backend="psutil", include_children=True, multiprocess=True)
    uss = memory_usage(proc=func, max_usage=True, backend="psutil_uss", include_children=True, multiprocess=True)
    pss = memory_usage(proc=func, max_usage=True, backend="psutil_pss", include_children=True, multiprocess=True)
    print(rss, uss, pss)


def test_multiprocessing_write():

    import numpy as np
    import joblib
    import time

    def func():
        n_jobs = 4
        a = np.random.random((size, size))

        def subprocess(i):
            aa = a.copy()
            time.sleep(2)
            return aa[i,i]

        results = joblib.Parallel(n_jobs=n_jobs)(
            joblib.delayed(subprocess)(i) 
            for i in range(n_jobs))

        return results

    rss = memory_usage(proc=func, max_usage=True, backend="psutil", include_children=True, multiprocess=True)
    uss = memory_usage(proc=func, max_usage=True, backend="psutil_uss", include_children=True, multiprocess=True)
    pss = memory_usage(proc=func, max_usage=True, backend="psutil_pss", include_children=True, multiprocess=True)
    print(rss, uss, pss)


def test_multiprocessing_showcase():

    import numpy as np
    import joblib
    import time
    import datetime

    def func():

        # n_jobs = 32
        # size = 25000
        # Creating data: 25000x25000 ... done (4.66 Gb). Starting processing: n_jobs=32 ... done (0:00:37.581291). RSS: 353024.01
        # Creating data: 25000x25000 ... done (4.66 Gb). Starting processing: n_jobs=32 ... done (0:00:38.867385). USS: 148608.62
        # Creating data: 25000x25000 ... done (4.66 Gb). Starting processing: n_jobs=32 ... done (0:00:29.049754). PSS: 169253.91

        # n_jobs = 64
        # size = 10000
        # Creating data: 10000x10000 ... done (0.75 Gb). Starting processing: n_jobs=64 ... done (0:00:14.701243). RSS: 111362.79
        # Creating data: 10000x10000 ... done (0.75 Gb). Starting processing: n_jobs=64 ... done (0:00:15.020202). USS: 56108.69
        # Creating data: 10000x10000 ... done (0.75 Gb). Starting processing: n_jobs=64 ... done (0:00:15.072918). PSS: 54826.61
        
        # Conclusion:
        # * RSS is overestimating like crazy (I checked the actual memory usage using htop)

        n_jobs = 8
        size = 3000

        print(f"Creating data: {size}x{size} ... ", end="")
        a = np.random.random((size, size))
        print(f"done ({a.size * a.itemsize / 1024**3:.02f} Gb). ", end="")

        def subprocess(i):
            aa = a.copy()
            r = aa[1,1]
            aa = a.copy()
            time.sleep(10)
            return r
            
            # r = a[1,1]
            # # time.sleep(10)
            # return r
            
            pass

        start = datetime.datetime.now()
        print(f"Starting processing: n_jobs={n_jobs} ... ", end="")
        results = joblib.Parallel(n_jobs=n_jobs)(
            joblib.delayed(subprocess)(i) 
            for i in range(n_jobs))
        print(f"done ({datetime.datetime.now() - start}). ", end="")

        return results

    rss = memory_usage(proc=func, max_usage=True, backend="psutil", include_children=True, multiprocess=True)
    print(f"RSS: {rss:.02f}")
    uss = memory_usage(proc=func, max_usage=True, backend="psutil_uss", include_children=True, multiprocess=True)
    print(f"USS: {uss:.02f}")
    pss = memory_usage(proc=func, max_usage=True, backend="psutil_pss", include_children=True, multiprocess=True)
    print(f"PSS: {pss:.02f}")
    print(f"RSS: {rss:.02f}, USS: {uss:.02f}, PSS: {pss:.02f}")


if __name__ == "__main__":
    test_simple()
    test_multiprocessing()
    test_multiprocessing_write()
    test_multiprocessing_showcase()
