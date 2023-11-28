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
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ..state import State
    from ..discord import DiscordUser


class BanEntry:
    """
    Guild ban object.

    Parameters
    ----------
    state:
        State object.
    data:
        Ban data.

    Attributes
    ----------
    guild_id:
        id of the guild on where the ban is.
    user:
        Discord user object who got banned.
    reason:
        Ban reason. If provided.
        .. note::
            BanEntry object passed by discord websocket (event)
            does not contain information about the reason for the ban even if there was one.
    """

    __slots__ = ("guild_id", "user", "reason")

    def __init__(self, state: State, data: dict[str, Any]):
        self.guild_id: int = int(data["guild_id"])
        self.user: DiscordUser = state.create_user(data=data)
        self.reason: str | None = data.get("reason")

    def __repr__(self) -> str:
        return f"<BanEntry(guild_id={self.guild_id}, user_id={self.user.id})>"

    def __hash__(self) -> int:
        return hash((self.user.id, self.guild_id, self.reason))

    def __eq__(self, other: object) -> bool:
        return isinstance(other, self.__class__) and other.unique_id == self.unique_id

    def __ne__(self, other: object) -> bool:
        if isinstance(other, self.__class__):
            return other.unique_id != self.unique_id
        return True

    @property
    def unique_id(self) -> int:
        """
        Unique id of ban entry object.
        """
        return self.__hash__()
