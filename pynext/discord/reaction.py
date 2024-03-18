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
from typing import TYPE_CHECKING, AsyncIterable, Any, TypeVar, Generic

from .emoji import Emoji

if TYPE_CHECKING:
    from ..selfbot import SelfBot
    from ..discord import GuildMember, DiscordUser, Guild
    from .message import BaseMessage

MessageT = TypeVar("MessageT", bound="BaseMessage")


class MessageReaction(Generic[MessageT]):
    """
    MessageReaction object representation.

    Parameters
    ----------
    message:
        A message to which the reaction is assigned.
    data:
        Reaction data.

    Attributes
    ----------
    message: :class:`typing.TypeVar`
        A message to which the reaction is assigned.
    emoji: :class:`Emoji`
        Reaction emoji object.
    guild: Optional[:class:`Guild`]
        Guild where the reaction is.
    author_id: Optional[:class:`int`]
        Reaction author id.
    """

    __slots__ = ("message", "emoji", "guild", "author_id")

    def __init__(self, message: MessageT, data: dict[str, Any]) -> None:
        emoji_data: dict[str, Any] = data["emoji"]

        self.message: MessageT = message
        self.emoji: Emoji = Emoji(
            name=emoji_data["name"],
            emoji_id=emoji_data.get("id"),
            animated=emoji_data.get("animated", False),
        )
        self.guild: Guild | None = getattr(self.message, "guild", None)

        if author_id := data.get("author_id"):
            self.author_id: int | None = int(author_id)
        else:
            self.author_id: int | None = None

    def __repr__(self) -> str:
        return (
            f"<MessageReaction(message_id={self.message.id}, emoji={self.emoji.name})>"
        )

    def __hash__(self) -> int:
        return hash((self.message.id, self.emoji.unique_id, self.guild, self.author_id))

    def __eq__(self, other: object) -> bool:
        return isinstance(other, self.__class__) and other.unique_id == self.unique_id

    def __ne__(self, other: object) -> bool:
        if isinstance(other, self.__class__):
            return other.unique_id != self.unique_id
        return True

    @property
    def unique_id(self) -> int:
        """
        Unique id of message reaction.
        """
        return self.__hash__()

    async def users(self, user: SelfBot) -> AsyncIterable[GuildMember | DiscordUser]:
        """
        An asynchronous method of fetching people who reacted to a emoji.

        Parameters
        ----------
        user:
            Selfbot to send request.

        Raises
        ------
        HTTPTimeoutError
            Request reached http timeout limit.
        HTTPException
            Fetching users failed.
        NotFound
            Message or Reaction not found.
        Forbidden
            Selfbot doesn't have proper permissions.
        """
        data: list[dict[str, Any]] = await user.http.get_reactions(
            user=user,
            channel_id=self.message.channel_id,
            message_id=self.message.id,
            emoji=self.emoji.encode,
        )

        for user_data in data:
            if self.guild is None:
                member = user.state.create_user(data=user_data)
            else:
                member = user.state.create_guild_member(
                    guild=self.guild, data=user_data
                )
                self.guild._add_member(member)
            yield member

    async def remove(self, user: SelfBot, member_id: int | None = None) -> None:
        """
        Method to remove the reaction of the specified user.
        If none then the id of the selfbot is considered.

        Parameters
        ----------
        user:
            Selfbot to send request.
        member_id:
            Reaction author id. If none, the id of the selfbot is considered.

        Raises
        ------
        HTTPTimeoutError
            Request reached http timeout limit.
        HTTPException
            Removing reaction failed.
        NotFound
            Message or Reaction not found.
        Forbidden
            Selfbot doesn't have proper permissions.
        """
        await user.http.remove_reaction(
            user=user,
            channel_id=self.message.channel_id,
            message_id=self.message.id,
            emoji=self.emoji.encode,
            user_id=member_id or user.id,
        )
