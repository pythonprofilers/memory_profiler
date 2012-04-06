Memory Profiler
---------------
This is a python module for monitoring memory consumption of a process
as well as line-by-line analysis of memory consumption for python
programs.


Installation
------------
To install through easy_install or pip::

    $ easy_install -U line_profiler # pip install -U line_profiler

To install from source, download the package, extract and type::

    $ python setup.py install



Usage
-----
The line-by-line profiler is used much in the same way of the
line_profiler: you must first decorate the function you would like to
profile with @profile::

    @profile
    def my_func():
        a = np.zeros((100, 100))
        b = np.zeros((1000, 1000))
        c = np.zeros((10000, 1000))
        return a, b, c


then execute the code passing the option "-m memory_profiler" to the
python interpreter. If the file name was example.py, this would result
in::

    $ python -m line_profiler example.py

Output will follow::

    13.8 MB               a = np.zeros((100, 100))
    13.9 MB               b = np.zeros((1000, 1000))
    21.5 MB               c = np.zeros((10000, 1000))
    97.8 MB               return a, b, c


Bugs & wishlist
---------------
It currently prints the memory at line *before* the line has been
executed. It would be nice to print consumption after the line has
been executed. Maybe also print the increment in memory consumption.


Development
-----------
Latest sources are available from github:

    https://github.com/fabianp/memory_profiler


Author: Fabian Pedregosa <fabian@fseoane.net>
License: Simplified BSD
