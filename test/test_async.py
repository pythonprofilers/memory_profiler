import asyncio

import pytest

from memory_profiler import profile


@profile
async def my_func():
    a = [1] * (10 ** 6)
    b = [2] * (2 * 10 ** 7)
    await asyncio.sleep(1e-2)
    del b
    return 1, 2

@pytest.mark.asyncio
async def test_async_func():
    task = asyncio.create_task(my_func())
    res = await asyncio.gather(task)
    assert res, "function didn't return anything"
    assert len(res) > 0, "task didn't return anything"
    assert res == [(1, 2), ]

