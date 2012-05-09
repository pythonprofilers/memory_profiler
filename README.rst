Memory Profiler
---------------
This is a python module for monitoring memory consumption of a process
as well as line-by-line analysis of memory consumption for python
programs.

It's a pure python module and has the `psutil
<http://pypi.python.org/pypi/psutil>`_ module as optional (but highly
recommended) dependencies.


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

    $ python -m memory_profiler example.py

Output will follow::

    Line #    Mem usage  Increment   Line Contents
    ==============================================
         3                           @profile
         4     13.59 MB    0.00 MB   def my_func():
         5     13.68 MB    0.09 MB       a = np.zeros((100, 100))
         6     21.31 MB    7.63 MB       b = np.zeros((1000, 1000))
         7     97.61 MB   76.30 MB       c = np.zeros((10000, 1000))
         8     97.61 MB    0.00 MB       return a, b, c


The first column represents the line number of the code that has been
profiled, the second column (*Mem usage*) the memory usage of the
Python interpreter after that line has been executed. The third column
(*Increment*) represents the difference in memory of the current line
with respect to the last one. The last column (*Line Contents*) prints
the code that has been profiled.

Frequently Asked Questions
--------------------------

    * Q: How accurate are the results ?
    * A: This module gets the memory consumption by querying the
      operating system kernel about the ammount of memory the current
      process has allocated, which might be slightly different from
      the ammount of memory that is actually used by the Python
      interpreter. For this reason, the output is only an
      approximation, and might vary between runs.

    * Q: Does it work under windows ?
    * A: Yes, but you will need the
    `psutil <http://pypi.python.org/pypi/psutil>`_ module.



Bugs & wish list
---------------
...


Development
-----------
Latest sources are available from github:

    https://github.com/fabianp/memory_profiler


Authors
-------
This module was written by `Fabian Pedregosa <http://fseoane.net>`_
inspired by Robert Kern's `line profiler
<http://packages.python.org/line_profiler/>`_.

`Tom <http://tomforb.es/>`_ added windows support and speed improvements via the
`psutil <http://pypi.python.org/pypi/psutil>`_ module.


License
-------
Simplified BSD
