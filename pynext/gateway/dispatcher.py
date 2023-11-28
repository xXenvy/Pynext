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
from typing import TYPE_CHECKING, Callable, Coroutine, Any, Generic, TypeVar

from logging import Logger, getLogger
from asyncio import iscoroutinefunction, get_event_loop

from ..errors import FunctionIsNotCoroutine

if TYPE_CHECKING:
    from asyncio import AbstractEventLoop

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
    client:
        Client object.
    loop:
        Client loop.
    events:
        Registered events.
    logger:
        Logger for logging event registrations and running them.
    """

    __slots__ = ("client", "loop", "events", "logger")

    def __init__(self, client: ObjectT | None = None) -> None:
        self.client: ObjectT | None = client
        self.loop: AbstractEventLoop = get_event_loop()

        self.events: dict[str, Callable[..., Coroutine]] = {}
        self.logger: Logger = getLogger("pynext.gateway")

    def __repr__(self) -> str:
        return f"<Dispatcher(events={len(self.events)})>"

    def listen(self, event: str) -> Callable:
        """
        Method that can be used as a decorator to register events.

        **Example usage**
        .. literalinclude:: ../examples/events.py
            :lines: 30-42
            :language: python
            :dedent: 4

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
        for event in (
            self.events.get(event_name),
            getattr(self.client, event_name, None),
        ):
            if event is not None and iscoroutinefunction(event):
                self.logger.debug(f"Dispatching an event: {event_name}.")
                self.loop.create_task(event(*args, **kwargs))
