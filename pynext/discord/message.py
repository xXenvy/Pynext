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

from ..utils import Hashable, snowflake_time
from ..types import MessageReference
from ..errors import Forbidden, NotFound

from .reaction import MessageReaction, Emoji

if TYPE_CHECKING:
    from datetime import datetime

    from ..selfbot import SelfBot
    from ..state import State

    from .member import GuildMember
    from .discorduser import DiscordUser
    from .guild import Guild
    from .channel import DMChannel, TextChannel
    from .attachment import Attachment


class BaseMessage(Hashable):
    """
    Representation of the base message object.
    Contains attributes that both PrivateMessage and GuildMessage have.

    Parameters
    ----------
    state:
        State object.
    data:
        Message data.

    Attributes
    ----------
    channel:
        Channel the message is on.
    author:
        Message author.
    type:
        Message type.
    id:
        Id of the message.
    content:
        Content of the message.
    pinned:
        Whether the message is pinned.
    author_id:
        Id of the message author.
    channel_id:
        Id of the message channel.
    tts:
        Whether this was a TTS message.
    """

    __slots__ = (
        "_state",
        "_reactions",
        "channel",
        "author",
        "type",
        "id",
        "content",
        "pinned",
        "author_id",
        "channel_id",
        "tts",
    )

    def __init__(self, state: State, data: dict[str, Any]):
        self._state: State = state
        self._reactions: dict[int, MessageReaction] = {}

        self.channel: DMChannel | TextChannel = data["channel"]
        self.author: DiscordUser | GuildMember = data["user_author"]

        self.type: int | None = data.get("type")
        self.id: int = int(data["id"])
        self.content: str = data["content"]
        self.pinned: bool = data["pinned"]

        self.author_id: int = int(data["author"]["id"])
        self.channel_id: int = int(data["channel_id"])
        self.tts: bool = data["tts"]

    @property
    def created_at(self) -> datetime:
        """
        Datetime object of when the message was created.
        """
        return snowflake_time(self.id)

    @property
    def reactions(self) -> list[MessageReaction]:
        """
        List with all message reactions.
        """
        return list(self._reactions.values())

    def get_reaction(self, unique_id: int) -> MessageReaction | None:
        """
        Method to get message reaction from cache by unique id.

        Parameters
        ----------
        unique_id:
            Unique id of message reaction.
        """
        return self._reactions.get(unique_id)

    async def delete(self, user: SelfBot) -> None:
        """
        Method to delete message.

        Parameters
        ----------
        user:
            Selfbot to send request.

        Raises
        ------
        HTTPTimeoutError
            Request reached http timeout limit.
        HTTPException
            Deleting the message failed.
        NotFound
            Message not found.
        Forbidden
            Selfbot doesn't have proper permissions.
        """
        if isinstance(self, PrivateMessage) and user.id != self.author_id:
            raise Forbidden("You can't delete someone private message.")

        await self._state.http.delete_message(user, self.channel_id, self.id)

    async def edit(self, user: SelfBot, content: str) -> GuildMessage | PrivateMessage:
        """
        Method to edit message.

        Parameters
        ----------
        user:
            Selfbot to send request.
        content:
            New message content.

        Raises
        ------
        HTTPTimeoutError
            Request reached http timeout limit.
        HTTPException
            Editing the message failed.
        NotFound
            Message not found.
        Forbidden
            Selfbot doesn't have proper permissions.
        """
        message_data: dict[str, Any] = await self._state.http.edit_message(
            user, channel_id=self.channel_id, message_id=self.id, content=content
        )
        if guild := getattr(self, "guild", None):
            message_data["guild_id"] = guild.id

        message: GuildMessage | PrivateMessage | None = (
            await self._state.create_message_from_data(user=user, data=message_data)
        )
        if message is None:
            raise NotFound("Message not found.")

        return message

    async def add_reaction(self, user: SelfBot, emoji: Emoji | str) -> None:
        """
        Method to add new reaction to message.

        Parameters
        ----------
        user:
            Selfbot to send request.
        emoji:
            Reaction emoji.

        Raises
        ------
        HTTPTimeoutError
            Request reached http timeout limit.
        HTTPException
            Adding reaction failed.
        NotFound
            Message not found.
        Forbidden
            Selfbot doesn't have proper permissions.
        """
        if isinstance(emoji, str):
            emoji = emoji.strip("<>")

        await self._state.http.create_reaction(
            user=user,
            channel_id=self.channel_id,
            message_id=self.id,
            emoji=emoji.encode if isinstance(emoji, Emoji) else emoji,
        )

    async def remove_reaction(
        self, user: SelfBot, emoji: Emoji | str, member_id: int | None = None
    ) -> None:
        """
        Method to remove reaction from message.

        Parameters
        ----------
        user:
            Selfbot to send request.
        emoji:
            Reaction emoji to remove.
        member_id:
            Reaction author id. If none, the id of the selfbot is considered.

        Raises
        ------
        HTTPTimeoutError
            Request reached http timeout limit.
        HTTPException
            Removing the reaction failed.
        NotFound
            Message or Reaction not found.
        Forbidden
            Selfbot doesn't have proper permissions.
        """
        if isinstance(emoji, str) and "<" in emoji:
            emoji = emoji.strip("<>")

        await self._state.http.remove_reaction(
            user=user,
            channel_id=self.channel_id,
            message_id=self.id,
            emoji=emoji.encode if isinstance(emoji, Emoji) else emoji,
            user_id=member_id or user.id,
        )

    async def remove_reactions(self, user: SelfBot):
        """
        Method to remove all reaction from the message.

        Parameters
        ----------
        user:
            Selfbot to send request.

        Raises
        ------
        HTTPTimeoutError
            Request reached http timeout limit.
        HTTPException
            Removing the reactions failed.
        NotFound
            Message not found.
        Forbidden
            Selfbot doesn't have proper permissions.
        """
        await self._state.http.remove_all_reactions(
            user=user, channel_id=self.channel_id, message_id=self.id
        )

    async def reply(
        self, user: SelfBot, content: str, reply_mention: bool = True
    ) -> PrivateMessage | GuildMessage:
        """
        Method to reply message.

        Parameters
        ----------
        user:
            Selfbot to send request.
        content:
            Message content.
        reply_mention:
            Whether to mention the author of the message to which you are responding.

        Raises
        ------
        HTTPTimeoutError
            Request reached http timeout limit.
        HTTPException
            Replying to the message failed.
        NotFound
            Message not found.
        Forbidden
            Selfbot doesn't have proper permissions.
        """
        message_reference: MessageReference = MessageReference(
            channel_id=self.channel_id, message_id=self.id
        )

        message_data: dict[str, Any] = await self._state.http.send_message(
            user=user,
            channel_id=self.channel_id,
            message_content=content,
            message_reference=message_reference,
            reply_mention=reply_mention,
        )
        message: PrivateMessage | GuildMessage | None = (
            await self._state.create_message_from_data(user=user, data=message_data)
        )
        if message is None:
            raise NotFound("Message not found.")

        return message

    async def mark_unread(self, user: SelfBot):
        """
        Method to mark message as unread.

        Parameters
        ----------
        user:
            Selfbot to send request.

        Raises
        ------
        HTTPTimeoutError
            Request reached http timeout limit.
        HTTPException
            Marking a message as unread failed.
        NotFound
            Message not found.
        Forbidden
            Selfbot doesn't have proper permissions.
        """
        await self._state.http.unack_message(
            user=user, channel_id=self.channel_id, message_id=self.id
        )

    def _add_reaction(self, reaction: MessageReaction) -> None:
        self._reactions[reaction.unique_id] = reaction

    def _remove_reaction(self, reaction: MessageReaction) -> None:
        try:
            del self._reactions[reaction.unique_id]
        except ValueError:
            pass


class PrivateMessage(BaseMessage):
    """
    Representation of the PrivateMessage.
    Type of message that was sent in a dm channel.

    Parameters
    ----------
    state:
        State object.
    message_data:
        Message data.

    Attributes
    ----------
    channel: :class:`DMChannel`
        Channel the message is on.
    author: :class:`DiscordUser`
        Message author.
    type: Optional[:class:`int`]
        Message type.
    id: :class:`int`
        Id of the message.
    content: :class:`str`
        Content of the message.
    pinned: :class:`bool`
        Whether the message is pinned.
    author_id: :class:`int`
        Id of the message author.
    channel_id: :class:`int`
        Id of the message channel.
    tts: :class:`bool`
        Whether this was a TTS message.
    """

    __slots__ = ("attachments",)

    def __init__(self, state: State, message_data: dict[str, Any]):
        super().__init__(state=state, data=message_data)

        self.channel: DMChannel = message_data["channel"]
        self.author: DiscordUser = message_data["user_author"]
        self.attachments: list[Attachment] = []

        for reaction_data in message_data.get("reactions", []):
            reaction: MessageReaction[PrivateMessage] = MessageReaction(
                message=self, data=reaction_data
            )
            self._reactions[reaction.unique_id] = reaction

        for attachment_data in message_data.get('attachments', []):
            attachment: Attachment[PrivateMessage] = self._state.create_attachment(message=self, data=attachment_data)
            self.attachments.append(attachment)

    def __repr__(self) -> str:
        return f"<PrivateMessage(id={self.id}, author_id={self.author_id})>"


class GuildMessage(BaseMessage):
    """
    Representation of the GuildMessage.
    Type of message that was sent in a guild channel.

    Parameters
    ----------
    state:
        State object.
    message_data:
        Message data.

    Attributes
    ----------
    guild: :class:`Guild`
        Guild on which the message is posted.
    channel: :class:`TextChannel`
        Channel the message is on.
    author: :class:`GuildMember`
        Message author.
    type: Optional[:class:`int`]
        Message type.
    id: :class:`int`
        Id of the message.
    content: :class:`str`
        Content of the message.
    pinned: :class:`bool`
        Whether the message is pinned.
    author_id: :class:`int`
        Id of the message author.
    channel_id: :class:`int`
        Id of the message channel.
    tts: :class:`bool`
        Whether this was a TTS message.
    """

    __slots__ = ("guild", "attachments")

    def __init__(self, state: State, message_data: dict[str, Any]):
        super().__init__(state=state, data=message_data)

        self.guild: Guild = message_data["guild"]
        self.channel: TextChannel = message_data["channel"]
        self.author: GuildMember = message_data["user_author"]
        self.attachments: list[Attachment] = []

        for reaction_data in message_data.get("reactions", []):
            reaction: MessageReaction[GuildMessage] = MessageReaction(
                message=self, data=reaction_data
            )
            self._reactions[reaction.unique_id] = reaction

        for attachment_data in message_data.get('attachments', []):
            attachment: Attachment[GuildMessage] = self._state.create_attachment(message=self, data=attachment_data)
            self.attachments.append(attachment)

    def __repr__(self) -> str:
        return f"<GuildMessage(id={self.id}, author_id={self.author_id})>"
