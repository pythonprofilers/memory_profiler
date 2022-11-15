import asyncio
import sys

from memory_profiler import profile


@profile
async def my_func():
    a = [1] * (10 ** 6)
    b = [2] * (2 * 10 ** 7)
    await asyncio.sleep(1e-2)
    del b

async def main():
    task = asyncio.create_task(my_func())
    res = await asyncio.gather(task)

async def main_legacy():
    future = asyncio.ensure_future(my_func())
    res = await asyncio.gather(future)

if __name__ == '__main__':
    if sys.version_info >= (3, 7):
        asyncio.run(main())  # main loop
    else:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main_legacy())
