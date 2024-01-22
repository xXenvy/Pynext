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
Channel = Union[
    "GuildChannel", "TextChannel", "VoiceChannel", "CategoryChannel", "ThreadChannel"
]
Snowflake = Union[str, int]


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
    """
    SelfBot Authorization dataclass.

    Parameters
    ----------
    key:
        Selfbot authorization token.
    cookies:
        Selfbot http cookies.

        .. versionadded:: 1.1.0
    """

    key: KeyT
    cookies: str | None = None

    @property
    def headers(self) -> dict[str, str | KeyT]:
        if self.cookies is None:
            return {"authorization": self.key}

        return {"authorization": self.key, "Cookie": self.cookies}


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


@dataclass(repr=False)
class ApplicationCommandOption:
    """
    ApplicationCommandOption dataclass.

    .. versionadded:: 1.0.6

    Parameters
    ----------
    type:
        Option type.
    name:
        Option name.
    description:
        Option description.
    required:
        Whether the option is required.
    autocomplete:
        If autocomplete are enabled for this option.
    min_value:
        Min value of this option.
    max_value:
        Max value of this option.
    channel_types:
        If the option is a channel type, the channels shown will be restricted to these types.
    """

    type: int
    name: str
    description: str
    required: bool
    autocomplete: bool
    min_value: int | None = None
    max_value: int | None = None
    channel_types: list[int] | None = None

    def __repr__(self) -> str:
        repr_attr: str = ", ".join(
            f"{key}={value}"
            for key, value in self.__dict__.items()
            if value is not None
        )
        return f"ApplicationCommandOption({repr_attr})"


@dataclass
class InteractionPayload:
    """
    Dataclass Payload passed in the ``on_interaction`` events.

    .. versionadded:: 1.0.8

    Parameters
    ----------
    nonce:
        Interaction nonce.
    id:
        Id of the interaction.
    """

    nonce: int
    id: int


@dataclass
class ThreadMembersUpdatePayload:
    """
    Dataclass Payload passed in the ``on_thread_members_update`` event.

    .. versionadded:: 1.2.0

    Parameters
    ----------
    thread:
        Thread on which the payload was received.
    added_members:
        List with added members.
    removed_members:
        List with removed members.
    """

    thread: ThreadChannel
    added_members: list[GuildMember]
    removed_members: list[int]


@dataclass
class SelectMenuOption:
    """
    SelectMenuOption dataclass.

    .. versionadded:: 1.3.0

    Parameters
    ----------
    label:
        Option label.
    value:
        Option value.
    description:
        Option description.
    emoji:
        Option emoji.
    default:
        Whether the option is default.
    """
    label: str
    value: str
    description: str | None = None
    emoji: Emoji | None = None
    default: bool = False
