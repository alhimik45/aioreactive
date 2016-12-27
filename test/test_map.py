import pytest
import asyncio
from typing import TypeVar
from asyncio import Future

from aioreactive.testing import VirtualTimeEventLoop
from aioreactive.core.operators.from_iterable import from_iterable
from aioreactive.core import run, subscribe, AnonymousAsyncObserver, AsyncStream
from aioreactive.core.operators import pipe as op


@pytest.yield_fixture()
def event_loop():
    loop = VirtualTimeEventLoop()
    yield loop
    loop.close()


@pytest.mark.asyncio
async def test_map_happy():
    xs = from_iterable([1, 2, 3])  # type: AsyncObservable[int]
    values = []

    async def asend(value):
        values.append(value)

    def mapper(value: int) -> int:
        return value * 10

    ys = xs | op.map(mapper)

    result = await run(ys, AnonymousAsyncObserver(asend))

    assert result == 30
    assert values == [10, 20, 30]


@pytest.mark.asyncio
async def test_map_mapper_throws():
    xs = from_iterable([1])
    exception = None
    error = Exception("ex")

    async def asend(value):
        pass

    async def athrow(ex):
        nonlocal exception
        exception = ex

    def mapper(x):
        raise error

    ys = xs | op.map(mapper)

    try:
        await run(ys, AnonymousAsyncObserver(asend, athrow))
    except Exception as ex:
        assert ex == error

    assert exception == error


@pytest.mark.asyncio
async def test_map_subscription_cancel():
    xs = AsyncStream()
    result = []
    sub = None

    def mapper(value):
        return value * 10

    print("-----------------------")
    print([xs, op.map])
    ys = xs | op.map(mapper)

    async def asend(value):
        result.append(value)
        sub.dispose()
        await asyncio.sleep(0)

    async with subscribe(ys, AnonymousAsyncObserver(asend)) as sub:

        await xs.asend(10)
        await asyncio.sleep(0)
        await xs.asend(20)

    assert result == [100]
