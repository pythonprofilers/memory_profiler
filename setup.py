import memory_profiler
from distutils.core import setup

CLASSIFIERS = """\
Development Status :: 4 - Beta
Intended Audience :: Science/Research
Intended Audience :: Developers
License :: OSI Approved
Programming Language :: Python
Programming Language :: Python :: 3
Topic :: Software Development
Operating System :: POSIX
Operating System :: Unix

"""

setup(
    name='memory_profiler',
    description='A module for getting memory usage of a python program',
    long_description=open('README.rst').read(),
    version=memory_profiler.__version__,
    author='Fabian Pedregosa',
    author_email='fabian@fseoane.net',
    url='http://pypi.python.org/pypi/memory_profiler',
	py_modules=['memory_profiler'],
    classifiers=[_f for _f in CLASSIFIERS.split('\n') if _f],

)