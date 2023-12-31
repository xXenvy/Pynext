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
from aiohttp import WSMessage, WSMsgType

from ..utils import json_loads
from ..enums import GatewayCodes, Events
from ..selfbot import SelfBot


class GatewayResponse:
    """
    Gateway response object.

    Parameters
    ----------
    response:
        Raw aiohttp gateway response.
    user:
        Selfbot, which received this response.

    Attributes
    ----------
    raw_data: :class:`dict`
        Raw websocket response.
    user: :class:`SelfBot`
        Selfbot, which received this response.
    type: :class:`aiohttp.WSMsgType`
        Aiohttp response type.
    op: :class:`int`
        Discord op code.
    data: :class:`dict`
        Raw gateway data.
    sequence: Optional[:class:`int`]
        Discord sequence.
    event_name: Optional[:class:`str`]
        Name received event.
    """

    __slots__ = ("type", "user", "op", "data", "sequence", "event_name", "raw_data")

    def __init__(self, response: WSMessage, user: SelfBot):
        self.raw_data: dict = json_loads(response.data)

        self.user: SelfBot = user
        self.type: WSMsgType = response.type

        self.op: int = self.raw_data["op"]
        self.data: dict = self.raw_data["d"]
        self.sequence: int | None = self.raw_data["s"]
        self.event_name: str | None = self._format_event_name(self.raw_data.get("t"))

        if self.event_name == "on_thread_member_update":
            self.event_name = "on_thread_members_update"

    def __repr__(self) -> str:
        return f"GatewayResponse(op={self.op}, sequence={self.sequence})"

    @property
    def event(self) -> bool:
        """
        Whether the response is event.
        """
        return self.op == GatewayCodes.DISPATCH.value and bool(self.event_name)

    @staticmethod
    def _format_event_name(event_name: str | None) -> str | None:
        """
        Method to format event name.
        """
        if event_name is None:
            return None

        converter: dict[str, str] = {event.name: event.value for event in Events}
        return converter.get(event_name)
