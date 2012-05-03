Memory Profiler
---------------
This is a python module for monitoring memory consumption of a process
as well as line-by-line analysis of memory consumption for python
programs.


Installation
------------
To install through easy_install or pip::

    $ easy_install -U memory_profiler # pip install -U memory_profiler

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
python interpreter to load the memory_profiler module and print to
stdout the line-by-line analysis. If the file name was example.py,
this would result in::

    $ python -m memory_profiler -l -v example.py

Output will follow::

    Line #    Mem usage   Line Contents
    ===================================
         3                @profile
         4     14.19 MB   def my_func():
         5     14.27 MB       a = np.zeros((100, 100))
         6     21.91 MB       b = np.zeros((1000, 1000))
         7     98.20 MB       c = np.zeros((10000, 1000))
         8     98.20 MB       return a, b, c




Bugs & wishlist
---------------
Maybe also print the increment in memory consumption.


Development
-----------
Latest sources are available from github:

    https://github.com/fabianp/memory_profiler


Authors
-------
This module was written by `Fabian Pedregosa <http://fseoane.net>`_ inspired by Robert Kern's
`line profiler <http://packages.python.org/line_profiler/>`_.

`Tom <http://tomforb.es/>`_ added windows support and speed improvements via the
`psutil <http://pypi.python.org/pypi/psutil>`_ module.


License
-------
Simplified BSD
