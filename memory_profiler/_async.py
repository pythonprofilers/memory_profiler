from asyncio import coroutine, iscoroutinefunction
from functools import wraps

from .line_profiler import (
    get_profile_wrapper as default_profile_wrapper,
    LineProfiler,
)
from .utils import show_results


class CoroLineProfiler(LineProfiler):
    def wrap_function(self, func):
        if iscoroutinefunction(func):
            @coroutine
            def f(*args, **kwargs):
                with self.count_ctxmgr():
                    yield from func(*args, **kwargs)
            return f
        else:
            return super().wrap_function(func)


def get_profile_wrapper(func, precision, backend, stream):
    if iscoroutinefunction(func):
        @wraps(func)
        @coroutine
        def wrapper(*args, **kwargs):
            prof = CoroLineProfiler(backend=backend)
            val = yield from prof(func)(*args, **kwargs)
            show_results(prof, stream=stream, precision=precision)
            return val
    else:
        wrapper = default_profile_wrapper(func, precision, backend, stream)

    return wrapper
