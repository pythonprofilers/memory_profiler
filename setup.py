import re
from setuptools import setup


# https://packaging.python.org/guides/single-sourcing-package-version/
def find_version(file_paths):
    with open(file_paths) as f:
        version_file = f.read()
    version_match = re.search(
        r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M
    )
    if version_match:
        return version_match.group(1)


CLASSIFIERS = """\
Development Status :: 5 - Production/Stable
Intended Audience :: Science/Research
Intended Audience :: Developers
License :: OSI Approved :: BSD License
Programming Language :: Python
Programming Language :: Python :: 3
Topic :: Software Development
Operating System :: POSIX
Operating System :: Unix

"""


setup(
    name='memory_profiler',
    description='A module for monitoring memory usage of a python program',
    long_description=open('README.rst').read(),
    version=find_version("memory_profiler.py"),
    author='Fabian Pedregosa',
    author_email='f@bianp.net',
    url='https://github.com/pythonprofilers/memory_profiler',
    py_modules=['memory_profiler', 'mprof'],
    entry_points={
        'console_scripts': ['mprof = mprof:main'],
    },
    install_requires=['psutil'],
    python_requires='>=3.4',
    classifiers=[_f for _f in CLASSIFIERS.split('\n') if _f],
    license='BSD'
)
