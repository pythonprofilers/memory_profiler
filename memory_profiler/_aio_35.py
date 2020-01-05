from functools import wraps
from inspect import iscoroutinefunction

from .line_profiler import (
    get_profile_wrapper as default_profile_wrapper,
    LineProfiler,
)
from .utils import show_results


class CoroLineProfiler(LineProfiler):
    def wrap_function(self, func):
        if iscoroutinefunction(func):
            async def f(*args, **kwargs):
                with self.count_ctxmgr():
                    return await func(*args, **kwargs)
            return f
        else:
            return super().wrap_function(func)


def get_profile_wrapper(func, precision, backend, stream):
    if iscoroutinefunction(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            prof = CoroLineProfiler(backend=backend)
            val = await prof(func)(*args, **kwargs)
            show_results(prof, stream=stream, precision=precision)
            return val
    else:
        wrapper = default_profile_wrapper(func, precision, backend, stream)

    return wrapper
