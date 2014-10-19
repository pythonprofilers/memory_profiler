import memory_profiler
from distutils.core import setup
import setuptools

CLASSIFIERS = """\
Development Status :: 5 - Production/Stable
Intended Audience :: Science/Research
Intended Audience :: Developers
License :: OSI Approved :: BSD License
Programming Language :: Python
Programming Language :: Python :: 2
Programming Language :: Python :: 2.6
Programming Language :: Python :: 2.7
Programming Language :: Python :: 3
Programming Language :: Python :: 3.2
Programming Language :: Python :: 3.3
Topic :: Software Development
Operating System :: POSIX
Operating System :: Unix

"""

setup(
    name='memory_profiler',
    description='A module for monitoring memory usage of a python program',
    long_description=open('README.rst').read(),
    version=memory_profiler.__version__,
    author='Fabian Pedregosa',
    author_email='f@bianp.net',
    url='http://pypi.python.org/pypi/memory_profiler',
    py_modules=['memory_profiler'],
    scripts=['mprof'],
    classifiers=[_f for _f in CLASSIFIERS.split('\n') if _f],
    license='BSD'

)
