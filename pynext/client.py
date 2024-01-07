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
from typing import ClassVar

from asyncio import AbstractEventLoop, get_event_loop
from logging import getLogger, Logger
from aiohttp import ClientTimeout

from .rest import HTTPClient
from .selfbot import SelfBot
from .gateway import WebSocketConnector, Dispatcher


class PynextClient:
    """
    Main class for connecting selfbots to gateway and rest api.

    Parameters
    ----------
    request_delay:
        Delay between sending requests to rest api.

        .. warning::
            I don't recommend changing this below 0.1s, as Discord may block your account for unnatural behavior.

    ratelimit_delay:
        Additional ratelimit delay, which is added when you reach ratelimit.
    chunk_guilds:
        Whether the client should chunk guilds of each selfbot.
        In a large number of servers or selfbots, this can make the startup much longer.
    chunk_channels:
        Whether the client should chunks guild channels.

        .. note::
            This parameter is considered only when ``chunk_guilds`` is True.

    http_timeout:
        Parameter to manage HTTP connection timeout.
    debug_events:
        Whether the client should run debug events such as: on_websocket_raw_receive.
    reconnect:
        Whether the client should automatically reconnect to the gateway.

    Attributes
    ----------
    gateway: :class:`WebSocketConnector`
        Websocket connector used to connect gateway and register events.
    loop: :class:`asyncio.AbstractEventLoop`
        Client event loop.
    dispatcher: :class:`Dispatcher`
        Major client dispatcher.
    """

    __version__: ClassVar[str] = "1.1.0"
    __slots__ = ("gateway", "loop", "dispatcher", "_http", "_users", "_logger")

    def __init__(
        self,
        request_delay: float = 0.1,
        ratelimit_delay: float = 0.5,
        chunk_guilds: bool = True,
        chunk_channels: bool = True,
        http_timeout: ClientTimeout = ClientTimeout(total=10),
        debug_events: bool = False,
        reconnect: bool = True,
    ):
        self.gateway: WebSocketConnector = WebSocketConnector(
            client=self,
            chunk_guilds=chunk_guilds,
            chunk_channels=chunk_channels,
            debug_events=debug_events,
            reconnect=reconnect
        )
        self.loop: AbstractEventLoop = get_event_loop()
        self.dispatcher: Dispatcher[PynextClient] = Dispatcher(client=self)

        self._http: HTTPClient = HTTPClient(
            request_delay, ratelimit_delay, self.dispatcher, http_timeout
        )
        self._logger: Logger = getLogger("pynext.common")
        self._users: set[SelfBot] = set()

    @property
    def users(self) -> list[SelfBot]:
        """
        A list with connected selfbots.
        """
        return list(self._users)

    async def login(self, *auths: str) -> None:
        """
        Method to check the provided tokens and create SelfBot objects.

        .. note::
            The method will not connect users to the gateway.

        Parameters
        ----------
        auths:
            Tokens used to authenticate selfbots.

        Raises
        ------
        RuntimeError
            HTTP Session is not defined.
        """
        for token in set(auths):
            if data := await self._http.login_request(token):
                user: SelfBot = SelfBot(token=token, user_data=data, http=self._http)

                self._users.add(user)
                self._logger.info(f"Connected to the account: {user}.")
                self.dispatcher.dispatch("on_user_login", user)

            else:
                self._logger.error(f"Invalid token: {token}. SelfBot not found.")

    async def setup(self, *tokens: str) -> None:
        """
        Async method that creates selfbots and connects them to the gateway.

        Parameters
        ----------
        tokens:
            Tokens used to authenticate selfbots.
        """
        self._logger.info(f"Running client, {len(set(tokens))} tokens loaded.")

        await self._http.setup()
        await self.login(*tokens)
        await self.gateway.start()

    def run(self, *tokens: str) -> None:
        """
        Sync method that runs the :func:`setup` method in a loop.

        Parameters
        ----------
        tokens:
            Tokens used to authenticate selfbots.
        """
        self.loop.run_until_complete(self.setup(*tokens))
