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

After installing the module, if you use IPython, you can set up the `%mprun`
and `%memit` magics by following these steps.

For IPython 0.10, you can install it by editing the IPython configuration
file ~/.ipython/ipy_user_conf.py to add the following lines::

    # These two lines are standard and probably already there.
    import IPython.ipapi
    ip = IPython.ipapi.get()

    # These two are the important ones.
    import memory_profiler    
    ip.expose_magic('mprun', memory_profiler.magic_mprun)
    ip.expose_magic('memit', memory_profiler.magic_memit)prun)

For IPython 0.11+, you have to  create a file named
~/.ipython/extensions/memory_profiler_ext.py with the following content::

    import memory_profiler
     
    def load_ipython_extension(ip):
        ip.define_magic('mprun', memory_profiler.magic_mprun)
        ip.define_magic('memit', memory_profiler.magic_memit)

If you don't have an IPython profile already set up, create one using the
following command::

    $ ipython profile create

Then, edit the configuration file for your IPython profile,
~/.ipython/profile_default/ipython_config.py, to register the extension like
this (If you already have other extensions, just add this one to the list)::

    c.TerminalIPythonApp.extensions = [
        'memory_profiler_ext',
    ]
    c.InteractiveShellApp.extensions = [
        'memory_profiler_ext',
    ]

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

The same output can be obtained in IPython by using the `%mprun` magic command.
In this case, you can skip the `@profile` decorator and instead use the
`-f` parameter, like this::

    In [1] from example import my_func

    In [2] %mprun -f my_func my_func()

Another useful magic that we define is `%memit`, which is analogous to
`%timeit`. It can be used as follows::

    In [1]: import numpy as np

    In [2]: %memit np.zeros(1e7)
    maximum of 3: 76.402344 MB per loop

For more details, see the docstrings of the magics.

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
<http://stackoverflow.com/>`_ and add the *profiling* tag.
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

`Victor <https://github.com/octavo>`_ added python3, bugfixes and general
cleanup.

`Vlad Niculae <http://vene.ro/>`_ added the `%mprun` and `%memit` IPython magics. 



=========
 License
=========
Simplified BSD
