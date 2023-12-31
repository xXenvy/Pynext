"""
The MIT License (MIT)
Copyright (c) 2023-present xXenvy

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""
from __future__ import annotations
from typing import (
    TYPE_CHECKING,
    Callable,
    Coroutine,
    Any,
    Generic,
    TypeVar,
    Awaitable,
    Union,
)

from logging import Logger, getLogger
from asyncio import iscoroutinefunction, get_event_loop, Future
from collections import defaultdict

from ..utils import maybe_coro
from ..errors import FunctionIsNotCoroutine

if TYPE_CHECKING:
    from asyncio import AbstractEventLoop

    WaitForCheck = Callable[..., Union[Awaitable[bool], bool]]


ObjectT = TypeVar("ObjectT", bound=object)


class Dispatcher(Generic[ObjectT]):
    """
    Representation of the dispatcher.
    Which provides a way to register events and running them.

    Parameters
    ----------
    client:
        An object for running events in a class.

    Attributes
    ----------
    client: Optional[:class:`ObjectT`]
        Client object.
    loop: :class:`asyncio.AbstractEventLoop`
        Client loop.
    events: :class:`dict`
        Registered events.
    logger: :class:`logging.Logger`
        Logger for logging event registrations and running them.
    """

    __slots__ = ("client", "loop", "events", "logger", "_wait_for_futures")

    def __init__(self, client: ObjectT | None = None) -> None:
        self.client: ObjectT | None = client
        self.loop: AbstractEventLoop = get_event_loop()

        self.events: dict[str, Callable[..., Coroutine]] = {}
        self.logger: Logger = getLogger("pynext.gateway")
        self._wait_for_futures: dict[
            str, list[tuple[Future, WaitForCheck | None]]
        ] = defaultdict(list)

    def __repr__(self) -> str:
        return f"<Dispatcher(events={len(self.events)})>"

    def listen(self, event: str) -> Callable:
        """
        Method that can be used as a decorator to register events.

        Parameters
        ----------
        event:
            Event name to register.

        Raises
        ------
        FunctionIsNotCoroutine
            Function of the event is not asynchronous.
        """

        def wrapper(function: Callable) -> None:
            if not iscoroutinefunction(function):
                raise FunctionIsNotCoroutine(
                    f"Event function: {function} must be asynchronous."
                )

            self.register(event_name=event.lower(), function=function)

        return wrapper

    def register(self, event_name: str, function: Callable[..., Coroutine]) -> None:
        """
        Method to register events.

        Parameters
        ----------
        event_name:
            Event name to register.
        function:
            Function linked to an event.

        Raises
        ------
        FunctionIsNotCoroutine
            Function of the event is not asynchronous.
        """
        if not iscoroutinefunction(function):
            raise FunctionIsNotCoroutine(
                f"Event function: {function} must be asynchronous."
            )

        self.events[event_name] = function
        self.logger.debug(f"Dispatcher registered new event: {event_name}.")

    def dispatch(self, event_name: str, *args: Any, **kwargs: Any) -> None:
        """
        Method to run events.

        Parameters
        ----------
        event_name:
            Event to run.
        args:
            Event args.
        kwargs:
            Event kwargs.
        """
        event_name = event_name.lower()
        for future, check in self._wait_for_futures.get(event_name, []):
            self.logger.debug(f"Dispatching an wait_for: {event_name}.")

            self.loop.create_task(
                self._run_future(event_name, future, check, *args, **kwargs)
            )

        for event in (
            self.events.get(event_name),
            getattr(self.client, event_name, None),
        ):
            if event is not None and iscoroutinefunction(event):
                self.logger.debug(f"Dispatching an event: {event_name}.")
                self.loop.create_task(event(*args, **kwargs))

    async def wait_for(
        self, event_name: str, check: WaitForCheck | None = None
    ) -> tuple[Any, ...]:
        """
        Async method to wait until the specified event has been called.

        **Example usage:**

        .. code-block:: python

            selfbot, message = await dispatcher.wait_for(
                event_name='on_message_create',
                check=lambda user, msg: msg.content == 'Hello'
            )
            await message.reply(selfbot, 'Hi!')

        Parameters
        ----------
        event_name:
            Name of the event.
        check:
            Optional check which must be True for the event to return a result.
        """
        event_name = event_name.lower()
        future: Future = Future()

        self._wait_for_futures[event_name].append((future, check))
        result = await future
        return result

    async def _run_future(
        self,
        event_name: str,
        future: Future,
        check: WaitForCheck | None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        if check is not None:
            result: bool = await maybe_coro(check, *args, **kwargs)
            if not result:
                return

        future.set_result(tuple(args) + tuple(kwargs.values()))
        self._wait_for_futures[event_name].remove((future, check))
