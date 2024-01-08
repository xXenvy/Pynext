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
from typing import TYPE_CHECKING, Any, ClassVar, Callable

from logging import Logger, getLogger
from aiohttp import ClientWebSocketResponse

from asyncio import gather, Queue, Task, sleep, create_task, Event
from time import time, perf_counter
from warnings import warn

from ..utils import json_dumps
from ..enums import GatewayCodes
from ..errors import WebsocketNotConnected

from .response import GatewayResponse
from .dispatcher import Dispatcher
from .parser import Parser

if TYPE_CHECKING:
    from ..client import PynextClient
    from ..selfbot import SelfBot


class WebSocketConnector:
    """
    WebSocketConnector, which connects selfbots to discord gateway.

    Parameters
    ----------
    client:
        Pynext client.
    chunk_guilds:
        Whether the client should chunk guilds of each selfbot.
    chunk_channels:
        Whether the client should chunks guild channels.
    debug_events:
        Whether the client should run debug events such as: on_websocket_raw_receive.

    Attributes
    ----------
    client: :class:`PynextClient`
        Pynext client.
    chunk_guilds: :class:`bool`
        Whether the client should chunk guilds of each selfbot.
    chunk_channels: :class:`bool`
        Whether the client should chunks guild channels.
    debug_events: :class:`bool`
        Whether the client should run debug events such as: on_websocket_raw_receive.
    """

    __slots__ = (
        "client",
        "chunk_guilds",
        "chunk_channels",
        "debug_events",
        "_logger",
        "_websockets",
    )

    gateway_url: ClassVar[str] = "wss://gateway.discord.gg/?v=10&encoding=json"

    def __init__(
        self,
        client: PynextClient,
        chunk_guilds: bool,
        chunk_channels: bool,
        debug_events: bool,
    ):
        self.client: PynextClient = client
        self.chunk_guilds: bool = chunk_guilds
        self.chunk_channels: bool = chunk_channels
        self.debug_events: bool = debug_events

        self._websockets: dict[SelfBot, DiscordWebSocket] = {}
        self._logger: Logger = getLogger("pynext.gateway")

    @property
    def websockets(self) -> dict[SelfBot, DiscordWebSocket]:
        """
        A dictionary with websocket connections.

        .. versionadded:: 1.2.0
        """
        return self._websockets

    def get_websocket(self, user: SelfBot) -> DiscordWebSocket | None:
        """
        Method to get websocket connection for user.

        .. versionadded:: 1.2.0
        """
        return self._websockets.get(user)

    def add_websocket(self, websocket: DiscordWebSocket) -> None:
        """
        Method to add websocket to the connector.

        .. versionadded:: 1.2.0
        """
        websocket.connected.set()
        websocket.user.gateway = websocket
        self._websockets[websocket.user] = websocket

    def remove_websocket(self, websocket: DiscordWebSocket) -> None:
        """
        Method to remove websocket from the connector.

        .. versionadded:: 1.2.0
        """
        try:
            del self._websockets[websocket.user]
            websocket.connected.clear()
        except KeyError:
            pass

    async def start(self, reconnect: bool = False):
        """
        Asynchronous method to connect selfbots to gateway.

        Parameters
        ----------
        reconnect:
            Whether websocket should reconnect if the connection breaks.
        """
        tasks: list[Task] = []

        self._logger.debug(
            f"Creating a gateway connection for {len(self.client.users)} users..."
        )

        for user in self.client.users:
            websocket: DiscordWebSocket = DiscordWebSocket(user=user, connector=self)
            task: Task = self.client.loop.create_task(websocket.run(self.gateway_url))
            tasks.append(task)

        await gather(*tasks)

    def event(self, event_name: str) -> Callable:
        """
        Method used as decorator for event registration.

        Parameters
        ----------
        event_name:
            Event name to register.

        # TODO: Remove this method in the future and change 'gateway' attribute to 'connector' in PynextClient.
        """
        warn(
            "Using client.gateway.event is deprecated. Use client.dispatcher.listen instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.client.dispatcher.listen(event_name)


class DiscordWebSocket:
    """
    DiscordWebSocket class supports a single connection to the Discord gateway.

    Parameters
    ----------
    user:
        Selfbot assigned to the connection.

    Attributes
    ----------
    user: :class:`SelfBot`
        Selfbot that is supposed to be connected to the gateway.
    websocket: Optional[:class:`aiohttp.ClientWebSocketResponse`]
        Aiohttp websocket connection.
    dispatcher: :class:`Dispatcher`
        Client master dispatcher.
    connected: :class:`asyncio.Event`
        Asyncio event that determines whether the selfbot has been connected.
    latency: :class:`float`
        Websocket latency value.
    """

    __slots__ = (
        "user",
        "websocket",
        "dispatcher",
        "connected",
        "latency",
        "connector",
        "_request_queue",
        "_last_send",
        "_client",
        "_last_sequence",
        "_pulse",
        "_logger",
        "_parser",
        "_debug_events",
    )

    def __init__(
        self,
        user: SelfBot,
        connector: WebSocketConnector,
    ) -> None:
        self.user: SelfBot = user
        self.websocket: ClientWebSocketResponse | None = None
        self.connected: Event = Event()

        self.connector: WebSocketConnector = connector
        self.dispatcher: Dispatcher[PynextClient] = connector.client.dispatcher
        self.latency: float = 0.0

        self._parser: Parser = Parser(
            chunk_guilds=connector.chunk_guilds, chunk_channels=connector.chunk_channels
        )
        self._request_queue: Queue[dict[str, Any]] = Queue()
        self._client: PynextClient = connector.client
        self._debug_events: bool = connector.debug_events

        self._logger: Logger = getLogger("pynext.gateway")
        self._pulse: int = 10
        self._last_send: float = perf_counter()
        self._last_sequence: int | None = None
        # For now, we are not using last_sequence,
        # however we will need it to resume the connection to the gateway in the future.

    @property
    def websocket_status(self) -> bool:
        """
        Websocket status.
        """
        if not self.websocket:
            return False

        return not self.websocket.closed

    def is_connected(self) -> bool:
        """
        Determines whether selfbot is connected to the gateway.
        """
        return self.connected.is_set()

    async def disconnect(self) -> None:
        """
        An asynchronous method to disconnect a websocket connection.
        """
        if self.websocket_status is True:
            assert isinstance(self.websocket, ClientWebSocketResponse)

            self._logger.info("Closing gateway connection...")

            self.connector.remove_websocket(self)
            await self.websocket.close()

    async def run(self, gateway_url: str) -> None:
        """
        Asynchronous method to connect websocket to discord gateway and run tasks.

        Parameters
        ----------
        gateway_url:
            Url to connect gateway.
        """
        self.websocket = await self.user.http.connect_to_gateway(url=gateway_url)
        self.connector.add_websocket(self)

        self._logger.info(f"Connected {self.user} to the discord gateway.")

        tasks = [
            create_task(self.__ping_loop()),
            create_task(self.__receive_loop()),
            create_task(self.__request_loop()),
        ]

        for task in tasks:
            await task

    async def send_as_json(self, data: dict[str, Any]) -> None:
        """
        Method to send request via websocket using json.

        Parameters
        ----------
        data:
            Data to send.

        Raises
        ------
        WebsocketNotConnected
            Somehow selfbot received a request to send, but there is no connection to the websocket.
        """
        if self.websocket_status is False:
            raise WebsocketNotConnected(
                "Received request to send, but websocket has no connection to discord!"
            )

        assert isinstance(self.websocket, ClientWebSocketResponse)
        await self.websocket.send_str(json_dumps(data))

    async def __receive_loop(self):
        """
        A loop that handles received responses from the websocket.
        """
        async for received_response in self.websocket:  # type: ignore
            response: GatewayResponse = GatewayResponse(received_response, self.user)

            if self._debug_events is True:
                self.dispatcher.dispatch("on_websocket_raw_receive", response)

            self._logger.debug(f"Websocket received response: {response} | {self.user}")

            if response.sequence:
                self._last_sequence = response.sequence

            if response.op == GatewayCodes.HELLO.value:
                self._pulse = response.data["heartbeat_interval"] / 1000
                await self._send_identify()
                continue

            if response.op == GatewayCodes.HEARTBEAT_ACK.value:
                ack: float = perf_counter()
                self.latency = ack - self._last_send
                self._logger.debug(
                    f"Received HEARTBEAT_ACK. Updating gateway latency ({self.latency})..."
                )

            if response.event and response.event_name:
                await self.__dispatch_event(response)

    async def __dispatch_event(self, response: GatewayResponse):
        """
        Method to dispatch received event from websocket.
        """
        assert isinstance(response.event_name, str)

        event_args: tuple[Any, ...] | None = await self._parser.parse_event_args(
            response
        )
        if event_args is not None:
            self.dispatcher.dispatch(response.event_name, *event_args)

    async def __request_loop(self):
        """
        A loop that handles sending requests to the websocket.
        """
        while self.websocket_status:
            request: dict[str, Any] = await self._request_queue.get()
            await self.send_as_json(request)

    async def __ping_loop(self):
        """
        A loop that keeps alive a connection to the gateway.
        """
        while self.websocket_status:
            self._logger.debug(f"Keeping alive gateway connection. {self.user}.")
            self._last_send = perf_counter()

            request: dict[str, Any] = {
                "op": GatewayCodes.HEARTBEAT.value,
                "d": int(time()),
            }
            await self._request_queue.put(request)

            await sleep(self._pulse)

    async def _send_identify(self):
        """
        Method to send an identify request after receiving the first HELLO response from the websocket.
        """
        os: str = "Windows Desktop"
        browser: str = "Chrome"
        device: str = "Windows"

        request: dict = {
            "op": GatewayCodes.IDENTIFY.value,
            "d": {
                "token": self.user.token,
                "capabilities": 4093,
                "properties": {"os": os, "browser": browser, "device": device},
                "compress": False,
            },
            "intents": 3276799,
        }

        self._logger.info(
            f"Received HELLO. Sending identify request to the gateway. {self.user}."
        )
        await self._request_queue.put(request)

    async def change_voice_state(
        self,
        guild_id: int,
        channel_id: int | None,
        self_mute: bool = False,
        self_deaf: bool = False,
    ):
        """
        A method to change the voice state on the guild.

        Parameters
        ----------
        guild_id:
            Id of the server on which we are changing the state.
        channel_id:
            Id of the voice channel on which we are changing the state.
        self_mute:
            Whether the selfbot should have a muted microphone.
        self_deaf:
            Whether selfbot should have a muted sound.
        """
        request: dict[str, Any] = {
            "op": GatewayCodes.VOICE_STATE.value,
            "d": {
                "guild_id": guild_id,
                "channel_id": channel_id,
                "self_mute": self_mute,
                "self_deaf": self_deaf,
            },
        }

        self._logger.debug(f"Changing voice state for {self.user}.")
        await self._request_queue.put(request)

    async def change_presence(self, request: dict[str, Any]):
        """
        A method to change selfbot presence.

        Parameters
        ----------
        request:
            Prepared request to be sent to change the presence of the selfbot.
        """
        self._logger.debug(f"Changing presence for {self.user}.")
        await self._request_queue.put(request)
