"""Profile the memory usage of a Python program"""

__version__ = '0.18'

_CMD_USAGE = "python -m memory_profiler script_file.py"

import time, sys, os, pdb
import warnings
import linecache
import inspect


try:
    import psutil

    def _get_memory(pid):
        process = psutil.Process(pid)
        try:
            mem = float(process.get_memory_info()[0]) / (1024 ** 2)
        except psutil.AccessDenied:
            mem = -1
        return mem


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
        raise NotImplementedError('The psutil module is required for non-unix '
                                  'platforms')


def memory_usage(proc=-1, interval=.1, timeout=None, run_in_place=False):
    """
    Return the memory usage of a process or piece of code

    Parameters
    ----------
    proc : {int, string, tuple}, optional
        The process to monitor. Can be given by a PID, by a string
        containing a filename or by a tuple. The tuple should contain
        three values (f, args, kw) specifies to run the function
        f(*args, **kw).  Set to -1 (default) for current process.

    interval : float, optional

    timeout : float, optional


    run_in_place : boolean, optional. False by default
        If False fork the process and retrieve timings from a different
        process. You shouldn't need to change this unless you are affected
        by this (http://blog.vene.ro/2012/07/04/on-why-my-memit-fails-on-osx)
        bug.

    Returns
    -------
    mm : list of integers, size less than num
        memory usage, in KB
    """
    ret = []

    if timeout is not None:
        max_iter = timeout / interval
    elif isinstance(proc, int):
        # external process and no timeout
        max_iter = 1
    else:
        # for a Python function wait until it finishes
        max_iter = float('inf')

    if str(proc).endswith('.py'):
        filename = _find_script(proc)
        with open(filename) as f:
            proc = f.read()
        raise NotImplementedError

    if isinstance(proc, (list, tuple)):

        if len(proc) == 1:
            f, args, kw = (proc[0], (), {})
        elif len(proc) == 2:
            f, args, kw = (proc[0], proc[1], {})
        elif len(proc) == 3:
            f, args, kw = (proc[0], proc[1], proc[2])
        else:
            raise ValueError
        try:
            import multiprocessing
        except ImportError:
            print ('WARNING: cannot import module `multiprocessing`. Forcing to'
                   ' run inplace.')
            # force inplace
            run_in_place = True
        if run_in_place:
            import threading
            main_thread = threading.Thread(target=f, args=args, kwargs=kw)
        else:
            main_thread = multiprocessing.Process(target=f, args=args, kwargs=kw)
        i = 0
        main_thread.start()
        pid = getattr(main_thread, 'pid', os.getpid())
        while i < max_iter and main_thread.is_alive():
            m = _get_memory(pid)
            ret.append(m)
            time.sleep(interval)
            i += 1
        main_thread.join()
    else:
        # external process
        if proc == -1:
            proc = os.getpid()
        if max_iter == -1:
            max_iter = 1
        for _ in range(max_iter):
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

    def __init__(self, **kw):
        self.functions = list()
        self.code_map = {}
        self.enable_count = 0
        self.max_mem = kw.get('max_mem', None)

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
            # func_code does not exist in Python3
            code = func.__code__
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
            exec(cmd, globals, locals)
        finally:
            self.disable_by_count()
        return self

    def runcall(self, func, *args, **kw):
        """ Profile a single function call.
        """
        # XXX where is this used ? can be removed ?
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
        """Callback for sys.settrace"""
        if event in ('line', 'return') and frame.f_code in self.code_map:
                lineno = frame.f_lineno
                if event == 'return':
                    lineno += 1
                entry = self.code_map[frame.f_code].setdefault(lineno, [])
                entry.append(_get_memory(os.getpid()))

        return self.trace_memory_usage

    def trace_max_mem(self, frame, event, arg):
        # run into PDB as soon as memory is higher than MAX_MEM
        if event in ('line', 'return') and frame.f_code in self.code_map:
            c = _get_memory(os.getpid())
            if c >= self.max_mem:
                t = 'Current memory {0:.2f} MB exceeded the maximum '.format(c) + \
                    'of {0:.2f} MB\n'.format(self.max_mem)
                sys.stdout.write(t)
                sys.stdout.write('Stepping into the debugger \n')
                frame.f_lineno -= 2
                p = pdb.Pdb()
                p.quitting = False
                p.stopframe = frame
                p.returnframe = None
                p.stoplineno = frame.f_lineno - 3
                p.botframe = None
                return p.trace_dispatch

        return self.trace_max_mem

    def __enter__(self):
        self.enable_by_count()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disable_by_count()

    def enable(self):
        if self.max_mem is not None:
            sys.settrace(self.trace_max_mem)
        else:
            sys.settrace(self.trace_memory_usage)

    def disable(self):
        self.last_time = {}
        sys.settrace(None)


def show_results(prof, stream=None):
    if stream is None:
        stream = sys.stdout
    template = '{0:>6} {1:>12} {2:>12}   {3:<}'

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
            if filename.startswith("ipython-input"):
                print("NOTE: %mprun can only be used on functions defined in "
                      "physical files, and not in the IPython environment.")
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
        for i in range(1, len(lines_normalized[keys[0] - 1])):
            lines_normalized[keys[0] - 1][i] = -1.
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
                mem = '{0:9.2f} MB'.format(mem)
                inc = '{0:9.2f} MB'.format(inc)
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
    options. The statistics will be shown side-by-side with the code through
    the pager once the statement has completed.

    Options:

    -f <function>: LineProfiler only profiles functions and methods it is told
    to profile.  This option tells the profiler about these functions. Multiple
    -f options may be used. The argument may be any expression that gives
    a Python function or method object. However, one must be careful to avoid
    spaces that may confuse the option parser. Additionally, functions defined
    in the interpreter at the In[] prompt or via %run currently cannot be
    displayed.  Write these functions out to a separate file and import them.

    One or more -f options are required to get any useful results.

    -T <filename>: dump the text-formatted statistics with the code
    side-by-side out to a text file.

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
        except Exception as e:
            raise UsageError('Could not find function %r.\n%s: %s' % (name,
                e.__class__.__name__, e))

    profile = LineProfiler()
    map(profile, funcs)
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
    print(message,)

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
        print('\n*** Profile printout saved to text file %s. %s' % (text_file,
                                                                    message))

    return_value = None
    if 'r' in opts:
        return_value = profile

    return return_value


def _func_exec(stmt, ns):
    # helper for magic_memit, just a function proxy for the exec
    # statement
    exec(stmt, ns)

# a timeit-style %memit magic for IPython
def magic_memit(self, line=''):
    """Measure memory usage of a Python statement

    Usage, in line mode:
      %memit [-ir<R>t<T>] statement

    Options:
    -r<R>: repeat the loop iteration <R> times and take the best result.
    Default: 1

    -i: run the code in the current environment, without forking a new process.
    This is required on some MacOS versions of Accelerate if your line contains
    a call to `np.dot`.

    -t<T>: timeout after <T> seconds. Unused if `-i` is active. Default: None

    Examples
    --------
    ::

      In [1]: import numpy as np

      In [2]: %memit np.zeros(1e7)
      maximum of 1: 76.402344 MB per loop

      In [3]: %memit np.ones(1e6)
      maximum of 1: 7.820312 MB per loop

      In [4]: %memit -r 10 np.empty(1e8)
      maximum of 10: 0.101562 MB per loop

      In [5]: memit -t 3 while True: pass;
      Subprocess timed out.
      Subprocess timed out.
      Subprocess timed out.
      ERROR: all subprocesses exited unsuccessfully. Try again with the `-i`
      option.
      maximum of 1: -inf MB per loop

    """
    opts, stmt = self.parse_options(line, 'r:t:i', posix=False, strict=False)
    repeat = int(getattr(opts, 'r', 1))
    if repeat < 1:
        repeat == 1
    timeout = int(getattr(opts, 't', 0))
    if timeout <= 0:
        timeout = None
    run_in_place = hasattr(opts, 'i')

    mem_usage = memory_usage((_func_exec, (stmt, self.shell.user_ns)), timeout=timeout,
        run_in_place=run_in_place)

    if mem_usage:
        print('maximum of %d: %f MB per loop' % (repeat, max(mem_usage)))
    else:
        print('ERROR: could not read memory usage, try with a lower interval or more iterations')


def profile(func):
    def wrapper(*args, **kwargs):
        prof = LineProfiler()
        val = prof(func)(*args, **kwargs)
        show_results(prof)
        return val
    return wrapper


if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser(usage=_CMD_USAGE, version=__version__)
    parser.add_option("--pdb-mmem", dest="max_mem", metavar="MAXMEM",
        type="float", action="store",
        help="step into the debugger when memory exceeds MAXMEM")

    if not sys.argv[1:]:
        parser.print_help()
        sys.exit(2)

    (options, args) = parser.parse_args()

    prof = LineProfiler(max_mem=options.max_mem)
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
