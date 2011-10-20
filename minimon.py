"""Get process information"""

__version__ = '0.1-git'

_CMD_USAGE = "python -m minimon script_file.py"

import time, sys, os
import linecache

if sys.platform.startswith('linux'):
    # FIXME: kernel page size might vary between archs
    def _get_memory(pid):
        try:
            f = open('/proc/%s/statm' % pid)
            res = (int(f.read().split(' ')[1]) * 4) / 1024
            f.close()
            return res
        except IOError:
            return 0
else:
    # ..
    # .. better to be safe than sorry ..
    raise NotImplementedError

def memory(proc= -1, num= -1, interval=.1, locals={}):
    """
    Return the memory usage of a process or piece of code

    Parameters
    ----------
    proc : {int, string}
        The process to monitor. Can be given by a PID or by a string
        containing a filename or the code to be executed. Set to -1
        (default)for current process.

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
        memory usage, in MB
    """
    ret = []

    if isinstance(proc, str):
        if proc.endswith('.py'):
            f = open('proc', 'r')
            proc = f.read()
            f.close()
            # TODO: make sure script's directory is on sys.path
        from multiprocessing import Process
        def f(x, locals):
            # function interface for exec
            exec(x, locals)

        p = Process(target=f, args=(proc, locals))
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

def find_script(script_name):
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

def label(code):
    """ Return a (filename, first_lineno, func_name) tuple for a given code
    object.

    This is the same labelling as used by the cProfile module in Python 2.5.
    """
    if isinstance(code, str):
        return ('~', 0, code)    # built-in functions ('~' sorts at the end)
    else:
        return (code.co_filename, code.co_firstlineno, code.co_name)

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
        if event == 'line':
            if frame.f_code in self.code_map:
                filename = frame.f_globals['__file__']
                if filename == "<stdin>":
                    # FIXME ?
                    filename = "traceit.py"
                if (filename.endswith(".pyc") or
                    filename.endswith(".pyo")):
                    filename = filename[:-1]
                entry = self.code_map[frame.f_code].setdefault(frame.f_lineno, [])
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

    for code in prof.code_map:
        lines = prof.code_map[code]
        for l in sorted(lines.keys()):
            mem = str(max(lines[l]))
            line = linecache.getline(code.co_filename, l)
            print "%s MB %s" % (mem, (' ' * (10 - len(mem)) + line.rstrip()))

if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser(usage=_CMD_USAGE)
    parser.add_option('-o', '--outfile', dest='outfile',
        help='Save stats to <outfile>', default=None)
    parser.add_option('-v', '--visualize', action='store_true',
        dest='visualize', help='Visualize result at exit',
        default=False)
    parser.add_option('-l', '--line', action='store_true',
        dest='line', help='Do line-by-line timings',
        default=False)


    if not sys.argv[1:] or sys.argv[1] in ("--help", "-h"):
        parser.print_help()
        sys.exit(2)

    (options, args) = parser.parse_args()
    sys.argv[:] = args

    if options.line:
        prof = LineProfiler()
        import __builtin__
        __builtin__.__dict__['monitor'] = prof
        __file__ = find_script(args[0])
        execfile(__file__, locals(), locals())
        if options.visualize:
            show_results(prof)
