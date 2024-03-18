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
from ..enums import DefaultAvatar
from ..errors import NotFound, Forbidden, HTTPException, PynextError

from .message import PrivateMessage
from .image import Image

if TYPE_CHECKING:
    from datetime import datetime

    from ..selfbot import SelfBot
    from ..state import State
    from .channel import DMChannel


class DiscordUser(Hashable):
    """
    Represents the DiscordUser object.

    Parameters
    ----------
    state:
        State object.
    user_data:
        SelfBot raw data.

    Attributes
    ----------
    global_name: Optional[:class:`str`]
        User global name.
    username: :class:`str`
        User username.
    discriminator: :class:`str`
        User discriminator.
    avatar_id: Optional[:class:`str`]
        ID of the user avatar.
    id: :class:`int`
        User unique ID.
    bot: :class:`bool`
        Whether user is classified as a bot.
    """

    __slots__ = (
        "global_name",
        "username",
        "discriminator",
        "avatar_id",
        "id",
        "_state",
        "bot",
    )

    def __init__(self, state: State, user_data: dict[str, Any]):
        self._state: State = state

        if user_data.get("user"):
            data: dict = user_data["user"]
        else:
            data: dict = user_data

        self.id: int = int(data["id"])
        self.global_name: str | None = data.get("global_name")
        self.username: str = data["username"]
        self.bot: bool = user_data.get("bot", False)

        self.discriminator: str = data["discriminator"]
        self.avatar_id: str | None = data["avatar"]

    def __repr__(self) -> str:
        return f"<DiscordUser(username={self.username}, id={self.id})>"

    @property
    def created_at(self) -> datetime:
        """
        Datetime object when the user has been created.
        """
        return snowflake_time(self.id)

    @property
    def display_avatar(self) -> Image:
        """
        Displayed user avatar.
        """
        return self.avatar or self.default_avatar

    @property
    def avatar(self) -> Image | None:
        """
        Image object with the user's avatar.
        """
        if not self.avatar_id:
            return None

        return Image._from_user(
            state=self._state, user_id=self.id, avatar_id=self.avatar_id
        )

    @property
    def default_avatar(self) -> Image:
        """
        Default user avatar
        """
        if self.discriminator != "0":
            avatar_index: int = (self.id >> 22) % len(DefaultAvatar)
        else:
            avatar_index: int = int(self.discriminator) % 5

        return Image._from_default_index(state=self._state, avatar_id=str(avatar_index))

    async def fetch_dm_channel(self, user: SelfBot) -> DMChannel:
        """
        Method to fetch dm channel.

        Parameters
        ----------
        user:
            Selfbot with which you want to create a dm channel.

        Raises
        ------
        PynextError
            You trying to fetch a dm channel with yourself.
        HTTPTimeoutError
            Request reached http timeout limit.
        HTTPException
            Fetching the channel failed.
        NotFound
            Channel not found.
        Forbidden
            Selfbot doesn't have proper permissions.
        """
        if user.id == self.id:
            raise PynextError("I can't fetch my own dm channel.")

        channel: DMChannel | None = user.get_dm_channel(channel_id=self.id)
        if channel:
            return channel

        data: dict[str, Any] = await self._state.http.create_dm(user, user_id=self.id)
        channel = self._state.create_dm_channel(data=data)
        user._add_dm_channel(channel=channel)

        return channel

    async def send(self, user: SelfBot, content: str) -> PrivateMessage:
        """
        Method to send private message to discord user.

        Parameters
        ----------
        user:
            Selfbot which is supposed to send a message.
        content:
            Message content.

        Raises
        ------
        PynextError
            You trying to send a message to yourself.
        HTTPTimeoutError
            Request reached http timeout limit.
        HTTPException
            Sending the message failed.
        NotFound
            Channel not found.
        Forbidden
            Selfbot doesn't have proper permissions.
        """
        if user.id == self.id:
            raise PynextError("I can't send a message to myself.")

        try:
            channel: DMChannel = await self.fetch_dm_channel(user=user)
        except (NotFound, Forbidden, HTTPException):
            raise NotFound(f"DMChannel {self} not found.")

        return await channel.send(user, content=content)

    async def send_friend_request(self, user: SelfBot) -> None:
        """
        Method to send friend request to discord user.

        Parameters
        ----------
        user:
            Selfbot to send friend request.

        Raises
        ------
        PynextError
            You trying to send a friend request to yourself.
        HTTPTimeoutError
            Request reached http timeout limit.
        HTTPException
            Sending the request failed.
        NotFound
            SelfBot not found.
        Forbidden
            Selfbot doesn't have proper permissions.
        """
        if user.id == self.id:
            raise PynextError("I can't send friend request to myself.")

        await self._state.http.send_friend_request(user, user_id=self.id)

    async def remove_friend(self, user: SelfBot) -> None:
        """
        Method to remove a user from friends.

        Parameters
        ----------
        user:
            Selfbot which is supposed to remove the user from friends.

        Raises
        ------
        PynextError
            You are trying to remove yourself from your friends.
        HTTPTimeoutError
            Request reached http timeout limit.
        HTTPException
            Sending the request failed.
        NotFound
            SelfBot not found.
        Forbidden
            Selfbot doesn't have proper permissions.
        """
        if user.id == self.id:
            raise PynextError("I can't remove myself from my friends.")

        await self._state.http.remove_friend(user, user_id=self.id)
