from asyncio import coroutine, iscoroutinefunction
from contextlib import contextmanager
from functools import wraps

from memory_profiler import LineProfiler, show_results


class CoroLineProfiler(LineProfiler):
    @contextmanager
    def count_contextmgr(self):
        self.enable_by_count()
        try:
            yield
        finally:
            self.disable_by_count()

    def wrap_function(self, func):
        if iscoroutinefunction(func):
            @coroutine
            def f(*args, **kwargs):
                with self.count_contextmgr():
                    yield from func(*args, **kwargs)
            return f
        else:
            return super(CoroLineProfiler, self).wrap_function(func)


def _get_coro_wrapper(coro, backend, stream, precision):
    @wraps(coro)
    @coroutine
    def wrapper(*args, **kwargs):
        prof = CoroLineProfiler(backend=backend)
        val = yield from prof(coro)(*args, **kwargs)
        show_results(prof, stream=stream, precision=precision)
        return val
