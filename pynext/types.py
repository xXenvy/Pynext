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
from typing import TypedDict, TYPE_CHECKING, Union, TypeVar, Generic

from dataclasses import dataclass

KeyT = TypeVar("KeyT")

if TYPE_CHECKING:
    from .rest import Route
    from .selfbot import SelfBot
    from .discord import *


Message = Union["PrivateMessage", "GuildMessage"]
Channel = Union["GuildChannel", "TextChannel", "VoiceChannel", "CategoryChannel"]


class MessageReference(TypedDict):
    channel_id: int | str
    message_id: int | str


class OverwritePayload(TypedDict):
    id: int | str
    type: int
    allow: str
    deny: str


@dataclass
class Authorization(Generic[KeyT]):
    """
    SelfBot Authorization dataclass.

    Parameters
    ----------
    key:
        Selfbot authorization token.
    """

    key: KeyT

    @property
    def headers(self) -> dict[str, KeyT]:
        return {"authorization": self.key}


@dataclass
class RatelimitPayload:
    """
    Dataclass Payload passed in the ``on_http_ratelimit`` event.

    Parameters
    ----------
    retry_after:
        Time in seconds until ratelimit ends.

        .. warning::
            Time until ratelimit ends is without additional time given in the :class:`PynextClient` class.
    is_global:
        Whether ratelimit is global.
    route:
        Blocked http route.
    user:
        Selfbot that received ratelimit.
    """

    retry_after: float
    is_global: bool
    route: Route
    user: SelfBot | None = None


@dataclass
class EmojisUpdatePayload:
    """
    Dataclass Payload passed in the ``on_guild_emojis_update`` event.

    Parameters
    ----------
    guild:
        Guild on which the payload was received.
    added_emojis:
        List with added emojis.
    deleted_emojis:
        List with removed emojis.
    """

    guild: Guild
    added_emojis: list[Emoji]
    deleted_emojis: list[Emoji]
