"""
Get process information
"""
import time, sys, os

if sys.platform.startswith('linux'):
    def _get_memory(pid):
        try:
            with open('/proc/%s/statm' % pid) as f:
                return int(f.read().split(' ')[1])
        except IOError:
            return 0
else:
    # ..
    # .. better to be safe than sorry ..
    raise NotImplementedError

def memory(proc= -1, num= -1, interval=.1, locals={}):
    """
    Return the memory usage of a process of piece of code
    
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
            exec x in globals(), locals

        p = Process(target=f, args=(proc, locals))
        p.start()
        while p.is_alive(): # FIXME: or num
            ret.append(_get_memory(p.pid))
            time.sleep(interval)
    else:
        if proc == -1:
            proc = os.getpid()
        for _ in range(num):
            ret.append(_get_memory(p.pid))
            time.sleep(interval)
    return ret



