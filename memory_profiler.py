"""Profile the memory usage of a Python program"""

__version__ = '0.14'

_CMD_USAGE = "python -m memory_profiler script_file.py"

import time
import sys
import os
import warnings
import linecache
import inspect

try:
    import psutil

    def _get_memory(pid):
        process = psutil.Process(pid)
        return float(process.get_memory_info()[0]) / (1024 ** 2)

except ImportError:

    warnings.warn("psutil module not found. memory_profiler will be slow")

    import subprocess
    if os.name == 'posix':
        def _get_memory(pid):
            # ..
            # .. memory usage in MB ..
            # .. this should work on both Mac and Linux ..
            # .. subprocess.check_output appeared in 2.7, using Popen ..
            # .. for backwards compatibility ..
            out = subprocess.Popen(['ps', 'v', '-p', str(pid)],
                  stdout=subprocess.PIPE).communicate()[0].split(b'\n')
            try:
                vsz_index = out[0].split().index(b'RSS')
                return float(out[1].split()[vsz_index]) / 1024
            except:
                return -1
    else:
        raise NotImplementedError('The psutil module is required for non-unix platforms')


def memory_usage(proc=-1, num=-1, interval=.1):
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
        with open(filename) as f:
            proc = f.read()

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
        while p.is_alive():  # FIXME: or num
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

    print >> sys.stderr, 'Could not find script {0}'.format(script_name)
    raise SystemExit(1)


class LineProfiler:
    """ A profiler that records the amount of memory for each line """

    def __init__(self, *functions):
        self.functions = list(functions)
        self.code_map = {}
        self.enable_count = 0
        for func in functions:
            self.add_function(func)

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
            warnings.warn("Could not extract a code object for the object %r"
                          % (func,))
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

    def run(self, cmd):
        """ Profile a single executable statment in the main namespace.
        """
        import __main__
        dict = __main__.__dict__
        return self.runctx(cmd, dict, dict)

    def runctx(self, cmd, globals, locals):
        """ Profile a single executable statement in the given namespaces.
        """
        self.enable_by_count()
        try:
            exec cmd in globals, locals
        finally:
            self.disable_by_count()
        return self

    def runcall(self, func, *args, **kw):
        """ Profile a single function call.
        """
        self.enable_by_count()
        try:
            return func(*args, **kw)
        finally:
            self.disable_by_count()

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

        if event in ('line', 'return') and frame.f_code in self.code_map:
                lineno = frame.f_lineno
                if event == 'return':
                    lineno += 1
                entry = self.code_map[frame.f_code].setdefault(lineno, [])
                entry.append(_get_memory(os.getpid()))

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
    template = '{0:>6} {1:>12} {2:>10}   {3:<}'

    for code in prof.code_map:
        lines = prof.code_map[code]
        if not lines:
            # .. measurements are empty ..
            continue
        filename = code.co_filename
        if filename.endswith((".pyc", ".pyo")):
            filename = filename[:-1]
        stream.write('Filename: ' + filename + '\n\n')
        if not os.path.exists(filename):
            stream.write('ERROR: Could not find file ' + filename + '\n')
            continue
        all_lines = linecache.getlines(filename)
        sub_lines = inspect.getblock(all_lines[code.co_firstlineno - 1:])
        linenos = range(code.co_firstlineno, code.co_firstlineno +
                        len(sub_lines))
        lines_normalized = {}

        header = template.format('Line #', 'Mem usage', 'Increment',
                                 'Line Contents')
        stream.write(header + '\n')
        stream.write('=' * len(header) + '\n')
        # move everything one frame up
        keys = sorted(lines.keys())

        k_old = keys[0] - 1
        lines_normalized[keys[0] - 1] = lines[keys[0]]
        k = keys.pop(0)
        while keys:
            lines_normalized[k] = lines[keys[0]]
            for i in range(len(lines_normalized[k_old]),
                           len(lines_normalized[k])):
                lines_normalized[k][i] = -1.
            k_old = k
            k = keys.pop(0)

        first_line = sorted(lines_normalized.keys())[0]
        mem_old = max(lines_normalized[first_line])
        for i, l in enumerate(linenos):
            mem = ''
            inc = ''
            if l in lines_normalized:
                mem = max(lines_normalized[l])
                inc = mem - mem_old
                mem_old = mem
                mem = '{0:5.4f} MB'.format(mem)
                inc = '{0:5.4f} MB'.format(inc)
            stream.write(template.format(l, mem, inc, sub_lines[i]))
        stream.write('\n\n')


# A lprun-style %mprun magic for IPython.
def magic_mprun(self, parameter_s=''):
    """ Execute a statement under the line-by-line memory profiler from the
    memory_profilser module.

    Usage:
      %mprun -f func1 -f func2 <statement>

    The given statement (which doesn't require quote marks) is run via the
    LineProfiler. Profiling is enabled for the functions specified by the -f
    options. The statistics will be shown side-by-side with the code through the
    pager once the statement has completed.

    Options:

    -f <function>: LineProfiler only profiles functions and methods it is told
    to profile.  This option tells the profiler about these functions. Multiple
    -f options may be used. The argument may be any expression that gives
    a Python function or method object. However, one must be careful to avoid
    spaces that may confuse the option parser. Additionally, functions defined
    in the interpreter at the In[] prompt or via %run currently cannot be
    displayed.  Write these functions out to a separate file and import them.

    One or more -f options are required to get any useful results.

    -T <filename>: dump the text-formatted statistics with the code side-by-side
    out to a text file.

    -r: return the LineProfiler object after it has completed profiling.
    """
    from StringIO import StringIO

    # Local imports to avoid hard dependency.
    from distutils.version import LooseVersion
    import IPython
    ipython_version = LooseVersion(IPython.__version__)
    if ipython_version < '0.11':
        from IPython.genutils import page
        from IPython.ipstruct import Struct
        from IPython.ipapi import UsageError
    else:
        from IPython.core.page import page
        from IPython.utils.ipstruct import Struct
        from IPython.core.error import UsageError

    # Escape quote markers.
    opts_def = Struct(T=[''], f=[])
    parameter_s = parameter_s.replace('"', r'\"').replace("'", r"\'")
    opts, arg_str = self.parse_options(parameter_s, 'rf:T:', list_all=True)
    opts.merge(opts_def)
    global_ns = self.shell.user_global_ns
    local_ns = self.shell.user_ns

    # Get the requested functions.
    funcs = []
    for name in opts.f:
        try:
            funcs.append(eval(name, global_ns, local_ns))
        except Exception, e:
            raise UsageError('Could not find function %r.\n%s: %s' % (name,
                e.__class__.__name__, e))

    profile = LineProfiler(*funcs)
    # Add the profiler to the builtins for @profile.
    import __builtin__
    if 'profile' in __builtin__.__dict__:
        had_profile = True
        old_profile = __builtin__.__dict__['profile']
    else:
        had_profile = False
        old_profile = None
    __builtin__.__dict__['profile'] = profile

    try:
        try:
            profile.runctx(arg_str, global_ns, local_ns)
            message = ''
        except SystemExit:
            message = "*** SystemExit exception caught in code being profiled."
        except KeyboardInterrupt:
            message = ("*** KeyboardInterrupt exception caught in code being "
                "profiled.")
    finally:
        if had_profile:
            __builtin__.__dict__['profile'] = old_profile

    # Trap text output.
    stdout_trap = StringIO()
    show_results(profile, stdout_trap)
    output = stdout_trap.getvalue()
    output = output.rstrip()

    if ipython_version < '0.11':
        page(output, screen_lines=self.shell.rc.screen_length)
    else:
        page(output)
    print message,

#    dump_file = opts.D[0]
#    if dump_file:
#        profile.dump_stats(dump_file)
#        print '\n*** Profile stats pickled to file',\
#              `dump_file` + '.', message

    text_file = opts.T[0]
    if text_file:
        pfile = open(text_file, 'w')
        pfile.write(output)
        pfile.close()
        print '\n*** Profile printout saved to text file %s. %s' % (text_file,
                                                                    message)

    return_value = None
    if 'r' in opts:
        return_value = profile

    return return_value


# a timeit-style %memit magic for IPython
def magic_memit(self, line=''):
    """Measure memory usage of a Python statement

    Usage, in line mode:
      %memit [-r<R>] statement

    Options:
    -r<R>: repeat the loop iteration <R> times and take the best result.
    Default: 3

    -t<T>: timeout after <T> seconds. Default: None

    Examples
    --------
    ::

      In [1]: import numpy as np

      In [2]: %memit np.zeros(1e7)
      best of 3: 76.402344 MB per loop
      Out[2]: 76.40234375

      In [3]: %memit np.ones(1e6)
      best of 3: 7.820312 MB per loop
      Out[3]: 7.8203125

      In [4]: %memit -r 10 np.empty(1e8)
      best of 10: 0.101562 MB per loop
      Out[4]: 0.1015625

    """

    import multiprocessing as pr
    from multiprocessing.queues import SimpleQueue

    opts, stmt = self.parse_options(line, 'r:t:tcp:',
                                    posix=False, strict=False)
    repeat = int(getattr(opts, "r", 3))
    if repeat < 1:
        repeat == 1
    timeout = int(getattr(opts, "t", 0))
    if timeout <= 0:
        timeout = None

    ns = self.shell.user_ns

    def _get_usage(q, stmt, setup='pass', ns={}):
        from memory_profiler import memory_usage as _mu
        try:
            exec setup in ns
            _mu0 = _mu()[0]
            exec stmt in ns
            _mu1 = _mu()[0]
            q.put(_mu1 - _mu0)
        except:
            q.put(float('-inf'))

    q = SimpleQueue()
    # try once in the current process
    _get_usage(q, stmt, 'pass', ns)
    # try in child processes
    at_least_one_worked = False
    for _ in xrange(repeat):
        p = pr.Process(target=_get_usage, args=(q, stmt, 'pass', ns))
        p.start()
        p.join(timeout=timeout)
        if p.exitcode == 0:
            at_least_one_worked = True
        else:
            p.terminate()
            q.put(float('-inf'))

    if not at_least_one_worked:
        print 'ERROR: subprocesses failed, result may be inaccurate.'

    usages = [q.get() for _ in xrange(repeat)]
    usage = max(usages)
    print u"worst of %d: %f MB per loop" % (repeat, usage)


if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser(usage=_CMD_USAGE)

    if not sys.argv[1:]:
        parser.print_help()
        sys.exit(2)

    (options, args) = parser.parse_args()

    # .. remove memory_profiler from sys.argv ..
    sys.argv.pop(0)

    prof = LineProfiler()
    __file__ = _find_script(args[0])
    if sys.version_info[0] < 3:
        import __builtin__
        __builtin__.__dict__['profile'] = prof
        execfile(__file__, locals(), locals())
    else:
        import builtins
        builtins.__dict__['profile'] = prof
        exec(compile(open(__file__).read(), __file__, 'exec'), locals(),
                                                               globals())

    show_results(prof)
