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
profile with ``@profile``. In this example, we create a simple function
``my_func`` that allocates lists ``a``, ``b`` and then deletes ``b``::


    @profile
    def my_func():
        a = [1] * (10 ** 6)
        b = [2] * (2 * 10 ** 7)
        del b
        return a

    if __name__ == '__main__':
        my_func()


Execute the code passing the option ``-m memory_profiler`` to the
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

Decorator
=========

A function decorator is also available.  Use as follows::

    from memory_profiler import profile

    @profile
    def my_func():
        a = [1] * (10 ** 6)
        b = [2] * (2 * 10 ** 7)
        del b
        return a

Setting debugger breakpoints
=============================
It is possible to set breakpoints depending on the amount of memory used.
That is, you can specify a threshold and as soon as the program uses more
memory than what is specified in the threshold it will stop execution
and run into the pdb debugger. To use it, you will have to decorate
the function as done in the previous section with ``@profile`` and then
run your script with the option ``-m memory_profiler --pdb-mmem=X``,
where X is a number representing the memory threshold in MB. For example::

    $ python -m memory_profiler --pdb-mmem=100 my_script.py

will run ``my_script.py`` and step into the pdb debugger as soon as the code
uses more than 100 MB in the decorated function.

.. TODO: alternatives to decoration (for example when you don't want to modify
    the file where your function lives).

=====
 API
=====
memory_profiler exposes a number of functions to be used in third-party
code.



``memory_usage(proc=-1, interval=.1, timeout=None)`` returns the memory usage
over a time interval. The first argument, ``proc`` represents what
should be monitored.  This can either be the PID of a process (not
necessarily a Python program), a string containing some python code to
be evaluated or a tuple ``(f, args, kw)`` containing a function and its
arguments to be evaluated as ``f(*args, **kw)``. For example,


    >>> from memory_profiler import memory_usage
    >>> mem_usage = memory_usage(-1, interval=.2, timeout=1)
    >>> print(mem_usage)
	[7.296875, 7.296875, 7.296875, 7.296875, 7.296875]


Here I've told memory_profiler to get the memory consumption of the
current process over a period of 1 second with a time interval of 0.2
seconds. As PID I've given it -1, which is a special number (PIDs are
usually positive) that means current process, that is, I'm getting the
memory usage of the current Python interpreter. Thus I'm getting
around 7MB of memory usage from a plain python interpreter. If I try
the same thing on IPython (console) I get 29MB, and if I try the same
thing on the IPython notebook it scales up to 44MB.


If you'd like to get the memory consumption of a Python function, then
you should specify the function and its arguments in the tuple ``(f,
args, kw)``. For example::


    >>> # define a simple function
    >>> def f(a, n=100):
        ...     import time
        ...     time.sleep(2)
        ...     b = [a] * n
        ...     time.sleep(1)
        ...     return b
        ...
    >>> from memory_profiler import memory_usage
    >>> memory_usage((f, (1,), {'n' : int(1e6)}))

This will execute the code `f(1, n=int(1e6))` and return the memory
consumption during this execution.


=====================
 IPython integration
=====================
After installing the module, if you use IPython, you can use the `%mprun`
and `%memit` magics.

For IPython 0.11+, you can use the module directly as an extension, with
``%load_ext memory_profiler``.

To activate it whenever you start IPython, edit the configuration file for your
IPython profile, ~/.ipython/profile_default/ipython_config.py, to register the
extension like this (If you already have other extensions, just add this one to
the list)::

    c.InteractiveShellApp.extensions = [
        'memory_profiler',
    ]

(If the config file doesn't already exist, run ``ipython profile create`` in
a terminal.)

It then can be used directly from IPython to obtain a line-by-line
report using the `%mprun` magic command. In this case, you can skip
the `@profile` decorator and instead use the `-f` parameter, like
this. Note however that function my_func must be defined in a file
(cannot have been defined interactively in the Python interpreter)::

    In [1] from example import my_func

    In [2] %mprun -f my_func my_func()

Another useful magic that we define is `%memit`, which is analogous to
`%timeit`. It can be used as follows::

    In [1]: import numpy as np

    In [2]: %memit np.zeros(1e7)
    maximum of 3: 76.402344 MB per loop

For more details, see the docstrings of the magics.

For IPython 0.10, you can install it by editing the IPython configuration
file ~/.ipython/ipy_user_conf.py to add the following lines::

    # These two lines are standard and probably already there.
    import IPython.ipapi
    ip = IPython.ipapi.get()

    # These two are the important ones.
    import memory_profiler
    ip.expose_magic('mprun', memory_profiler.magic_mprun)
    ip.expose_magic('memit', memory_profiler.magic_memit)

============================
 Frequently Asked Questions
============================
    * Q: How accurate are the results ?
    * A: This module gets the memory consumption by querying the
      operating system kernel about the amount of memory the current
      process has allocated, which might be slightly different from
      the amount of memory that is actually used by the Python
      interpreter. Also, because of how the garbage collector works in
      Python the result might be different between platforms and even
      between runs.

    * Q: Does it work under windows ?
    * A: Yes, but you will need the
      `psutil <http://pypi.python.org/pypi/psutil>`_ module.



===========================
 Support, bugs & wish list
===========================
For support, please ask your question on `stack overflow
<http://stackoverflow.com/>`_ and add the *profiling* tag.
Send issues, proposals, etc. to `github's issue tracker
<https://github.com/fabianp/memory_profiler/issues>`_ .

If you've got questions regarding development, you can email me
directly at fabian@fseoane.net

.. image:: http://fseoane.net/static/tux_memory_small.png


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

`Victor <https://github.com/octavo>`_ added python3 support, bugfixes and general
cleanup.

`Vlad Niculae <http://vene.ro/>`_ added the `%mprun` and `%memit` IPython magics.

`Thomas Kluyver <https://github.com/takluyver>`_ added the IPython extension.



=========
 License
=========
Simplified BSD
