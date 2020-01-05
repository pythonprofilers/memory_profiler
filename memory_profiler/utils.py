import linecache
import os
import sys
import warnings
import subprocess
import time

import psutil

from .common import HAS_TRACEMALLOC, PY2, TWO_20

if HAS_TRACEMALLOC:
    import tracemalloc


if PY2:
    def to_str(x):
        return x

    from future_builtins import filter
else:
    def to_str(x):
        return str(x)


def show_results(prof, stream=None, precision=1):
    if stream is None:
        stream = sys.stdout
    template = '{0:>6} {1:>12} {2:>12}   {3:<}'

    for (filename, lines) in prof.code_map.items():
        header = template.format('Line #', 'Mem usage', 'Increment',
                                 'Line Contents')

        stream.write(u'Filename: ' + filename + '\n\n')
        stream.write(header + u'\n')
        stream.write(u'=' * len(header) + '\n')

        all_lines = linecache.getlines(filename)

        float_format = u'{0}.{1}f'.format(precision + 4, precision)
        template_mem = u'{0:' + float_format + '} MiB'
        for (lineno, mem) in lines:
            if mem:
                inc = mem[0]
                mem = mem[1]
                mem = template_mem.format(mem)
                inc = template_mem.format(inc)
            else:
                mem = u''
                inc = u''
            tmp = template.format(lineno, mem, inc, all_lines[lineno - 1])
            stream.write(to_str(tmp))
        stream.write(u'\n\n')


def choose_backend(new_backend=None):
    """
    Function that tries to setup backend, chosen by user, and if failed,
    setup one of the allowable backends
    """

    _backend = 'no_backend'
    all_backends = [
        ('psutil', True),
        ('posix', os.name == 'posix'),
        ('tracemalloc', HAS_TRACEMALLOC),
    ]
    backends_indices = dict((b[0], i) for i, b in enumerate(all_backends))

    if new_backend is not None:
        all_backends.insert(0, all_backends.pop(backends_indices[new_backend]))

    for n_backend, is_available in all_backends:
        if is_available:
            _backend = n_backend
            break
    if _backend != new_backend and new_backend is not None:
        warnings.warn('{0} can not be used, {1} used instead'.format(
            new_backend, _backend))
    return _backend


def get_child_memory(process, meminfo_attr=None):
    """
    Returns a generator that yields memory for all child processes.
    """
    # Convert a pid to a process
    if isinstance(process, int):
        if process == -1: process = os.getpid()
        process = psutil.Process(process)

    if not meminfo_attr:
        # Use the psutil 2.0 attr if the older version isn't passed in.
        meminfo_attr = 'memory_info' if hasattr(process, 'memory_info') else 'get_memory_info'

    # Select the psutil function get the children similar to how we selected
    # the memory_info attr (a change from excepting the AttributeError).
    children_attr = 'children' if hasattr(process, 'children') else 'get_children'

    # Loop over the child processes and yield their memory
    try:
        for child in getattr(process, children_attr)(recursive=True):
            yield getattr(child, meminfo_attr)()[0] / TWO_20
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        # https://github.com/fabianp/memory_profiler/issues/71
        yield 0.0


def get_memory(pid, backend, timestamps=False, include_children=False, filename=None):
    # .. low function to get memory consumption ..
    if pid == -1:
        pid = os.getpid()

    def tracemalloc_tool():
        # .. cross-platform but but requires Python 3.4 or higher ..
        stat = next(filter(lambda item: str(item).startswith(filename),
                           tracemalloc.take_snapshot().statistics('filename')))
        mem = stat.size / TWO_20
        if timestamps:
            return mem, time.time()
        else:
            return mem

    def ps_util_tool():
        # .. cross-platform but but requires psutil ..
        process = psutil.Process(pid)
        try:
            # avoid using get_memory_info since it does not exists
            # in psutil > 2.0 and accessing it will cause exception.
            meminfo_attr = 'memory_info' if hasattr(process, 'memory_info') \
                else 'get_memory_info'
            mem = getattr(process, meminfo_attr)()[0] / TWO_20
            if include_children:
                mem += sum(get_child_memory(process, meminfo_attr))
            if timestamps:
                return mem, time.time()
            else:
                return mem
        except psutil.AccessDenied:
            pass
            # continue and try to get this from ps

    def posix_tool():
        # .. scary stuff ..
        if include_children:
            raise NotImplementedError((
                "The psutil module is required to monitor the "
                "memory usage of child processes."
            ))

        warnings.warn("psutil module not found. memory_profiler will be slow")
        # ..
        # .. memory usage in MiB ..
        # .. this should work on both Mac and Linux ..
        # .. subprocess.check_output appeared in 2.7, using Popen ..
        # .. for backwards compatibility ..
        out = subprocess.Popen(['ps', 'v', '-p', str(pid)],
                               stdout=subprocess.PIPE
                               ).communicate()[0].split(b'\n')
        try:
            vsz_index = out[0].split().index(b'RSS')
            mem = float(out[1].split()[vsz_index]) / 1024
            if timestamps:
                return mem, time.time()
            else:
                return mem
        except:
            if timestamps:
                return -1, time.time()
            else:
                return -1

    if backend == 'tracemalloc' and \
            (filename is None or filename == '<unknown>'):
        raise RuntimeError(
            'There is no access to source file of the profiled function'
        )

    tools = {'tracemalloc': tracemalloc_tool,
             'psutil': ps_util_tool,
             'posix': posix_tool}
    return tools[backend]()
