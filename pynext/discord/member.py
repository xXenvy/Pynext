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
from typing import TYPE_CHECKING, Any, Iterable

from datetime import datetime

from ..utils import str_to_datetime

from .discorduser import DiscordUser
from .role import Role
from .image import Image

if TYPE_CHECKING:
    from ..selfbot import SelfBot

    from .guild import Guild
    from .channel import VoiceChannel


class GuildMember(DiscordUser):
    """
    Represents the GuildMember object.

    Parameters
    ----------
    data:
        Member data.
    guild:
        Guild on which the member is on.

    Attributes
    ----------
    guild: :class:`Guild`
        Guild on which the member is on.
    nickname: Optional[:class:`str`]
        Guild user nickname.
    communication_disabled_until: Optional[:class:`datetime.datetime`]
        Datetime object until the user is muted. Or None if it is not.
    global_name: Optional[:class:`str`]
        Member global name.
    username: :class:`str`
        Member username.
    discriminator: :class:`str`
        SelfBot discriminator.
    avatar_id: Optional[:class:`str`]
        ID of the user avatar.
    id: :class:`int`
        Member unique ID.
    bot: :class:`bool`
        Whether user is classified as a bot.
    """

    __slots__ = (
        "guild",
        "_roles",
        "_muted",
        "nickname",
        "communication_disabled_until",
    )

    def __init__(self, data: dict[str, Any], guild: Guild):
        super().__init__(user_data=data, state=guild._state)

        self.guild: Guild = guild
        self.nickname: str | None = data.get("nick")

        self.communication_disabled_until: None | datetime = None
        if timeout_value := data.get("communication_disabled_until"):
            self.communication_disabled_until = str_to_datetime(timeout_value)

        self._roles: dict[int, Role] = {}

        for role_id in data.get("roles", []):
            if role := self.guild.get_role(int(role_id)):
                self._roles[role.id] = role

    def __repr__(self) -> str:
        return f"<GuildMember(username={self.guild_nickname}, id={self.id})>"

    @property
    def guild_nickname(self) -> str:
        """
        SelfBot nickname on the guild.
        """
        if self.nickname:
            return self.nickname

        return self.global_name or self.username

    @property
    def guild_avatar(self) -> Image | None:
        """
        SelfBot avatar on the guild.
        """
        if not self.avatar_id:
            return None

        return Image._from_guild_avatar(
            state=self._state,
            user_id=self.id,
            guild_id=self.guild.id,
            avatar_id=self.avatar_id,
        )

    @property
    def roles(self) -> list[Role]:
        """
        SelfBot roles on the guild.
        """
        return list(self._roles.values())

    def is_muted(self) -> bool:
        """
        Whether the user is muted.
        """
        if self.communication_disabled_until is None:
            return False

        return self.communication_disabled_until > datetime.utcnow()

    async def fetch_roles(self, user: SelfBot) -> list[Role]:
        """
        Method to fetch member roles.

        Parameters
        ----------
        user:
            Selfbot to send request.

        Raises
        ------
        HTTPTimeoutError
            Request reached http timeout limit.
        HTTPException
            Fetching the roles failed.
        NotFound
            User not found.
        Forbidden
            Selfbot doesn't have proper permissions.
        """
        data: dict[str, Any] = await user.http.fetch_member(
            user=user, guild_id=self.guild.id, member_id=self.id
        )

        self._roles = {}

        for role_id in data["roles"]:
            if role := self.guild.get_role(int(role_id)):
                self._roles[role.id] = role

        return self.roles

    async def edit(
        self,
        user: SelfBot,
        nick: str | None = None,
        roles_to_add: Iterable[Role] | None = None,
        roles_to_remove: Iterable[Role] | None = None,
        communication_disabled_until: datetime | None = None,
        voice_channel: VoiceChannel | None = None,
        mute: bool | None = None,
        deaf: bool | None = None,
    ) -> GuildMember:
        """
        Method to edit member.

        Parameters
        ----------
        user:
            Selfbot to send request.
        nick:
            User guild nickname.
        roles_to_add:
            Roles to add for the user.
        roles_to_remove:
            Roles to remove from the user.
        communication_disabled_until:
            When the user's timeout will expire and the user will be able to communicate in the guild again.
        voice_channel:
            Channel to move user to (if they are connected to voice).
        mute:
            Whether the user is muted in voice channels.
        deaf:
            Whether the user is deafened in voice channels.

        Raises
        ------
        HTTPTimeoutError
            Request reached http timeout limit.
        HTTPException
            Editing the member failed.
        NotFound
            Member not found.
        Forbidden
            Selfbot doesn't have proper permissions.
        """
        params: dict[str, Any] = {
            "nick": nick,
            "roles_to_add": roles_to_add,
            "roles_to_remove": roles_to_remove,
            "communication_disabled_until": communication_disabled_until,
            "voice_channel_id": voice_channel.id if voice_channel else None,
        }

        for key, value in params.copy().items():
            if value is None:
                """
                If a parameter has a value of None,
                we don't want it in the dict because it could overwrite an already set parameter.
                """
                del params[key]

        data: dict[str, Any] = await self._state.http.edit_member(
            user, guild_id=self.guild.id, member=self, params=params
        )
        return self._state.create_guild_member(guild=self.guild, data=data)

    async def add_roles(self, user: SelfBot, roles: Iterable[Role]) -> GuildMember:
        """
        Method to add roles to member.

        Parameters
        ----------
        user:
            Selfbot to send request.
        roles:
            Roles to add for the user.

        Raises
        ------
        HTTPTimeoutError
            Request reached http timeout limit.
        HTTPException
            Editing the member failed.
        NotFound
            Member or role not found.
        Forbidden
            Selfbot doesn't have proper permissions.
        """
        return await self.edit(user, roles_to_add=roles)

    async def remove_roles(self, user: SelfBot, roles: Iterable[Role]) -> GuildMember:
        """
        Method to remove roles from member.

        Parameters
        ----------
        user:
            Selfbot to send request.
        roles:
            Roles to remove from the user.

        Raises
        ------
        HTTPTimeoutError
            Request reached http timeout limit.
        HTTPException
            Editing the member failed.
        NotFound
            Member or role not found.
        Forbidden
            Selfbot doesn't have proper permissions.
        """
        return await self.edit(user, roles_to_remove=roles)

    async def mute(self, user: SelfBot, duration: datetime) -> GuildMember:
        """
        Method to mute a member for a specified period of time.

        Parameters
        ----------
        user:
            Selfbot to send request.
        duration:
            Datetime object to when a user should be muted.

        Raises
        ------
        HTTPTimeoutError
            Request reached http timeout limit.
        HTTPException
            Editing the member failed.
        NotFound
            Member not found.
        Forbidden
            Selfbot doesn't have proper permissions.
        """
        return await self.edit(user, communication_disabled_until=duration)

    async def unmute(self, user: SelfBot) -> GuildMember:
        """
        Method to unmute member.

        Parameters
        ----------
        user:
            Selfbot to send request.

        Raises
        ------
        HTTPTimeoutError
            Request reached http timeout limit.
        HTTPException
            Editing the member failed.
        NotFound
            Member not found.
        Forbidden
            Selfbot doesn't have proper permissions.
        """
        return await self.edit(user)

    async def move(self, user: SelfBot, voice_channel: VoiceChannel) -> GuildMember:
        """
        A method to move the user to voice channel. (if connected to the voice).

        Parameters
        ----------
        user:
            Selfbot to send request.
        voice_channel:
            Voice channel to move member.

        Raises
        ------
        HTTPTimeoutError
            Request reached http timeout limit.
        HTTPException
            Editing the member failed.
        NotFound
            Member or channel not found.
        Forbidden
            Selfbot doesn't have proper permissions.
        """
        return await self.edit(user, voice_channel=voice_channel)
