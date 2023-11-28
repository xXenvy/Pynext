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

KeyT = TypeVar('KeyT')

if TYPE_CHECKING:
    from discord_typings import Snowflake

    from .discord import *
    from .rest import Route
    from .selfbot import SelfBot


Message = Union['PrivateMessage', 'GuildMessage']
Channel = Union['GuildChannel', 'TextChannel', 'VoiceChannel', 'CategoryChannel']


class MessageReference(TypedDict):
    channel_id: Snowflake
    message_id: Snowflake


class OverwritePayload(TypedDict):
    id: Snowflake
    type: int
    allow: str
    deny: str


@dataclass
class Authorization(Generic[KeyT]):
    key: KeyT

    @property
    def headers(self) -> dict[str, KeyT]:
        return {"authorization": self.key}


@dataclass
class RatelimitPayload:
    retry_after: float
    is_global: bool
    route: Route
    user: SelfBot | None = None


@dataclass
class EmojisUpdatePayload:
    guild: Guild
    added_emojis: list[Emoji]
    deleted_emojis: list[Emoji]
