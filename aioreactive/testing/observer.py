import asyncio
import logging
from typing import Awaitable, Callable, List, Tuple, TypeVar

from aioreactive import AsyncAwaitableObserver
from aioreactive.notification import Notification, OnCompleted, OnError, OnNext
from aioreactive.utils import anoop

TSource = TypeVar("TSource")

log = logging.getLogger(__name__)


class AsyncTestObserver(AsyncAwaitableObserver[TSource]):
    """A recording AsyncAnonymousObserver.

    Records all values and events that happens and makes them available
    through the values property:

    The values are recorded as tuples:
        - sends: (time, T)
        - throws: (time, err)
        - close: (time,)

    Note: we will not see the difference between sent and thrown
    exceptions. This should however not be any problem, and we have
    decided to keep it this way for simplicity.
    """

    def __init__(
        self,
        asend: Callable[[TSource], Awaitable[None]] = anoop,
        athrow: Callable[[Exception], Awaitable[None]] = anoop,
        aclose: Callable[[], Awaitable[None]] = anoop,
    ):
        super().__init__(asend, athrow, aclose)
        self._values: List[Tuple[float, Notification[TSource]]] = []

        self._send = asend
        self._throw = athrow
        self._close = aclose

        # self._loop = asyncio.get_event_loop()

    async def asend(self, value: TSource):
        log.debug("AsyncAnonymousObserver:asend(%s)", value)
        time = self._loop.time()
        self._values.append((time, OnNext(value)))

        await super().asend(value)
        # await self._send(value)

    async def athrow(self, error: Exception):
        log.debug("AsyncAnonymousObserver:athrow(%s)", error)
        time = self._loop.time()
        self._values.append((time, OnError(error)))

        await super().athrow(error)
        # await self._throw(error)

    async def aclose(self):
        log.debug("AsyncAnonymousObserver:aclose()")

        time = self._loop.time()
        self._values.append((time, OnCompleted))

        await super().aclose()
        # await self._close()

    @property
    def values(self):
        return self._values
