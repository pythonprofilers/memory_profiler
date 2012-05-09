=================
 Memory Profiler
=================
This is a python module for monitoring memory consumption of a process
as well as line-by-line analysis of memory consumption for python
programs.

It's a pure python module and has the `psutil
<http://pypi.python.org/pypi/psutil>`_ module as optional (but highly
recommended) dependencies.


==============
 Installation
==============
To install through easy_install or pip::

    $ easy_install -U memory_profiler # pip install -U memory_profiler

To install from source, download the package, extract and type::

    $ python setup.py install



=======
 Usage
=======
The line-by-line profiler is used much in the same way of the
line_profiler: you must first decorate the function you would like to
profile with @profile. In this example, we create a simple function
*my_func* that allocates tuples a, b and then deletes b::


    @profile
    def my_func():
        a = [1] * (10 ** 6)
        b = [2] * (2 * 10 ** 7)
        del b
        return a

    if __name__ == '__main__':
        my_func()


execute the code passing the option "-m memory_profiler" to the
python interpreter to load the memory_profiler module and print to
stdout the line-by-line analysis. If the file name was example.py,
this would result in::

    $ python -m memory_profiler example.py

Output will follow::

    Line #    Mem usage  Increment   Line Contents
    ==============================================
         3                           @profile
         4      5.97 MB    0.00 MB   def my_func():
         5     13.61 MB    7.64 MB       a = [1] * (10 ** 6)
         6    166.20 MB  152.59 MB       b = [2] * (2 * 10 ** 7)
         7     13.61 MB -152.59 MB       del b
         8     13.61 MB    0.00 MB       return a


The first column represents the line number of the code that has been
profiled, the second column (*Mem usage*) the memory usage of the
Python interpreter after that line has been executed. The third column
(*Increment*) represents the difference in memory of the current line
with respect to the last one. The last column (*Line Contents*) prints
the code that has been profiled.

============================
 Frequently Asked Questions
============================

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



===========================
 Support, bugs & wish list
===========================
For support, please ask your question on `stack overflow
<http://stackoverflow.com/>`_ and tag it with the *memory-profiler*
keyword.
Send issues, proposals, etc. to `github's issue tracker
<https://github.com/fabianp/memory_profiler/issues>`_ .

If you've got questions regarding development, you can email me
directly at fabian@fseoane.net


=============
 Development
=============
Latest sources are available from github:

    https://github.com/fabianp/memory_profiler


=========
 Authors
=========
This module was written by `Fabian Pedregosa <http://fseoane.net>`_
inspired by Robert Kern's `line profiler
<http://packages.python.org/line_profiler/>`_.

`Tom <http://tomforb.es/>`_ added windows support and speed improvements via the
`psutil <http://pypi.python.org/pypi/psutil>`_ module.


=========
 License
=========
Simplified BSD
