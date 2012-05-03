"""Get process information"""

__version__ = '0.9'

_CMD_USAGE = "python -m memory_profiler script_file.py"

import time, sys, os, warnings
import linecache, inspect

try:
    import psutil
    
    def _get_memory(pid):
        process = psutil.Process(pid)
        return float(process.get_memory_info()[0]) / (1024 ** 2)

except ImportError:

    warnings.warn("psutil module not found. This module provides "
                  "speed enhacements and windows support")

    import subprocess
    if os.name == 'posix':
        def _get_memory(pid):
            # ..
            # .. memory usage in MB ..
            # .. this should work on both Mac and Linux ..
            # .. subprocess.check_output appeared in 2.7, using Popen ..
            # .. for backwards compatibility ..
            out = subprocess.Popen(['ps', 'v', '-p', str(pid)],
                  stdout=subprocess.PIPE).communicate()[0].split('\n')
            try:
                vsz_index = out[0].split().index('RSS')
                return float(out[1].split()[vsz_index]) / 1024
            except:
                return -1
    else:
        raise NotImplementedError('The psutil module is required for non-unix platforms')

def memory_usage(proc= -1, num= -1, interval=.1):
    """
    Return the memory usage of a process or piece of code

    Parameters
    ----------
    proc : {int, string, tuple}
        The process to monitor. Can be given by a PID or by a string
        containing a filename. A tuple containing (f, args, kwargs) specifies
        to run the function f(*args, **kwargs). Set to -1 (default)for
        current process.

    interval : int, optional

    num : int, optional
        Number of samples to generate. In the case of
        defaults to -1, meaning
        to wait until the process has finished if proc is a string or
        to get just one if proc is an integer.

    locals : dict
        Local variables.

    Returns
    -------
    mm : list of integers
        memory usage, in KB
    """
    ret = []

    if str(proc).endswith('.py'):
        filename = _find_script(proc)
        f = open(filename, 'r')
        proc = f.read()
        f.close()
        # TODO: make sure script's directory is on sys.path
        def f_exec(x, locals):
            # function interface for exec
            exec(x, locals)
        proc = (f_exec, (), {})

    if isinstance(proc, (list, tuple)):
        from multiprocessing import Process
        if len(proc) == 1:
            proc = (proc[0], (), {})
        elif len(proc) == 2:
            proc = (proc[0], proc[1], {})
        p = Process(target=proc[0], args=proc[1], kwargs=proc[2])
        p.start()
        while p.is_alive(): # FIXME: or num
            ret.append(_get_memory(p.pid))
            time.sleep(interval)
    else:
        if proc == -1:
            proc = os.getpid()
        if num == -1:
            num = 1
        for _ in range(num):
            ret.append(_get_memory(proc))
            time.sleep(interval)
    return ret

# ..
# .. utility functions for line-by-line ..

def _find_script(script_name):
    """ Find the script.

    If the input is not a file, then $PATH will be searched.
    """
    if os.path.isfile(script_name):
        return script_name
    path = os.getenv('PATH', os.defpath).split(os.pathsep)
    for dir in path:
        if dir == '':
            continue
        fn = os.path.join(dir, script_name)
        if os.path.isfile(fn):
            return fn

    print >> sys.stderr, 'Could not find script %s' % script_name
    raise SystemExit(1)


class LineProfiler:
    """ A profiler that records the amount of memory for each line """

    def __init__(self, *functions):
        self.functions = list(functions)
        self.code_map = {}
        self.enable_count = 0

    def __call__(self, func):
        self.add_function(func)
        f = self.wrap_function(func)
        f.__module__ = func.__module__
        f.__name__ = func.__name__
        f.__doc__ = func.__doc__
        f.__dict__.update(getattr(func, '__dict__', {}))
        return f

    def add_function(self, func):
        """ Record line profiling information for the given Python function.
        """
        try:
            code = func.func_code
        except AttributeError:
            import warnings
            warnings.warn("Could not extract a code object for the object %r" % (func,))
            return
        if code not in self.code_map:
            self.code_map[code] = {}
            self.functions.append(func)

    def wrap_function(self, func):
        """ Wrap a function to profile it.
        """
        def f(*args, **kwds):
            self.enable_by_count()
            try:
                result = func(*args, **kwds)
            finally:
                self.disable_by_count()
            return result
        return f

    def enable_by_count(self):
        """ Enable the profiler if it hasn't been enabled before.
        """
        if self.enable_count == 0:
            self.enable()
        self.enable_count += 1

    def disable_by_count(self):
        """ Disable the profiler if the number of disable requests matches the
        number of enable requests.
        """
        if self.enable_count > 0:
            self.enable_count -= 1
            if self.enable_count == 0:
                self.disable()

    def trace_memory_usage(self, frame, event, arg):

        if event in ('line', 'return'):
            if frame.f_code in self.code_map:
                lineno = frame.f_lineno
                if event == 'return':
                    lineno += 1
                entry = self.code_map[frame.f_code].setdefault(lineno, [])
                entry.append(_get_memory(os.getpid()))

        # why this is needed, I don't know
        return self.trace_memory_usage

    def __enter__(self):
        self.enable_by_count()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disable_by_count()

    def enable(self):
        sys.settrace(self.trace_memory_usage)

    def disable(self):
        self.last_time = {}
        sys.settrace(None)

def show_results(prof, stream=None):

    if stream is None:
        stream = sys.stdout
    template = '%6s %12s   %-s'
    header = template % ('Line #', 'Mem usage', 'Line Contents')
    stream.write(header + '\n')
    stream.write('=' * len(header) + '\n')

    for code in prof.code_map:
        lines = prof.code_map[code]
        filename = code.co_filename
        if (filename.endswith(".pyc") or
            filename.endswith(".pyo")):
            filename = filename[:-1]
        all_lines = linecache.getlines(filename)
        sub_lines = inspect.getblock(all_lines[code.co_firstlineno-1:])
        linenos = range(code.co_firstlineno, code.co_firstlineno + len(sub_lines))
        lines_normalized = {}

        # move everything one frame up
        keys = lines.keys()
        keys.sort()
        lines_normalized[code.co_firstlineno+1] = lines[keys[0]]
        while len(keys) > 1:
            v = keys.pop(0)
            lines_normalized[v] = lines[keys[0]]

        for l in linenos:
            mem = ''
            if lines_normalized.has_key(l):
                mem = '%5.2f MB' % max(lines_normalized.get(l))
            line = linecache.getline(filename, l)
            stream.write(template % (l, mem, line))

if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser(usage=_CMD_USAGE)
    parser.add_option('-o', '--outfile', dest='outfile',
        help='Save stats to <outfile>', default=None)
    parser.add_option('-v', '--visualize', action='store_true',
        dest='visualize', help='Visualize result at exit',
        default=True)
    parser.add_option('-l', '--line', action='store_true',
        dest='line', help='Do line-by-line timings',
        default=True)


    if not sys.argv[1:] or sys.argv[1] in ("--help", "-h"):
        parser.print_help()
        sys.exit(2)

    (options, args) = parser.parse_args()
    sys.argv[:] = args

    if options.line:
        prof = LineProfiler()
        __file__ = _find_script(args[0])
        if sys.version_info[0] < 3:
            import __builtin__
            __builtin__.__dict__['profile'] = prof
            execfile(__file__, locals(), locals())
        else:
            import builtins
            builtins.__dict__['profile'] = prof
            exec(compile(open(__file__).read(), __file__, 'exec'), locals(), globals())

        if options.visualize:
            show_results(prof)
