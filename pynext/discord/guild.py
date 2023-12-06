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
from typing import AsyncIterable

from ..utils import applications_filter
from .channel import *
from .reaction import Emoji

from .role import Role
from .image import Image
from .banentry import BanEntry

if TYPE_CHECKING:
    from datetime import datetime

    from .permissions import Permissions
    from .color import Color
    from .member import GuildMember
    from .application import Application

    from ..state import State
    from ..selfbot import SelfBot
    from ..types import Channel


class Guild(Hashable):
    """
    Represents the Guild object.

    Parameters
    ----------
    state:
        State object.
    data:
        Guild data.

    Attributes
    ----------
    id: :class:`int`
        Guild ID.
    name: :class:`str`
        Guild name.
    owner_id: :class:`int`
        Guild owner id.
    icon_id: Optional[:class:`str`]
        Guild icon id.
    afk_channel_id: Optional[:class:`int`]
        Id of afk channel.
    afk_timeout: :class:`int`
        Afk timeout in seconds.
    system_channel_id: Optional[:class:`int`]
        Id of the channel where guild notices such as welcome messages and boost events are posted.
    premium_progress_bar_enabled: :class:`bool`
        Whether the guild has the boost progress bar enabled.
    verification_level: :class:`int`
        Verification level required for the guild.
    preferred_locale: :class:`str`
        The preferred locale of a Community guild.
    premium_tier: :class:`int`
        Guild boost level.
    """

    __slots__ = (
        "_state",
        "id",
        "name",
        "owner_id",
        "icon_id",
        "afk_channel_id",
        "preferred_locale",
        "verification_level",
        "premium_tier",
        "system_channel_id",
        "afk_timeout",
        "premium_progress_bar_enabled",
        "_roles",
        "_channels",
        "_members",
        "_emojis",
        "_applications",
    )

    def __init__(self, state: State, data: dict[str, Any]):
        self._state: State = state

        self.id: int = int(data["id"])
        self.name: str = data["name"]
        self.owner_id: int = int(data["owner_id"])
        self.icon_id: str | None = data["icon"]

        self.afk_channel_id: int | None = (
            int(data["afk_channel_id"]) if data["afk_channel_id"] else None
        )
        self.afk_timeout: int = data["afk_timeout"]
        self.system_channel_id: int | None = (
            int(data["system_channel_id"]) if data["system_channel_id"] else None
        )

        self.premium_progress_bar_enabled: bool = data["premium_progress_bar_enabled"]
        self.verification_level: int = data["verification_level"]
        self.preferred_locale: str = data["preferred_locale"]
        self.premium_tier: int = data["premium_tier"]

        self._roles: dict[int, Role] = {}
        self._channels: dict[int, Channel] = {}
        self._members: dict[int, GuildMember] = {}
        self._emojis: set[Emoji] = set()
        self._applications: dict[int, Application] = {}

        for role_data in data["roles"]:
            role = Role(guild=self, data=role_data)

            self._roles[role.id] = role

        for emoji_data in data["emojis"]:
            emoji = Emoji(
                name=emoji_data["name"],
                animated=emoji_data["animated"],
                emoji_id=int(emoji_data["id"]),
            )

            self._emojis.add(emoji)

    def __repr__(self) -> str:
        return f"<Guild(name={self.name}, id={self.id})>"

    @property
    def owner(self) -> GuildMember | None:
        """
        GuildMember object of the guild owner.
        """
        return self._members.get(self.owner_id)

    @property
    def afk_channel(self) -> VoiceChannel | None:
        """
        VoiceChannel object of the afk channel.
        """
        if self.afk_channel_id is None:
            return None

        channel = self._channels.get(self.afk_channel_id)
        if channel is not None:
            assert isinstance(channel, VoiceChannel)

        return channel

    @property
    def system_channel(self) -> TextChannel | None:
        """
        TextChannel object of the system channel.
        """
        if self.system_channel_id is None:
            return None

        channel = self._channels.get(self.system_channel_id)
        if channel is not None:
            assert isinstance(channel, TextChannel)

        return channel

    @property
    def created_at(self) -> datetime:
        """
        A datetime object that determines when the guild was created.
        """
        return snowflake_time(self.id)

    @property
    def icon(self) -> Image | None:
        """
        Image object representing the guild icon.
        """
        if self.icon_id is None:
            return None

        return Image._from_guild_icon(
            state=self._state, guild_id=self.id, icon_id=self.icon_id
        )

    @property
    def emojis(self) -> list[Emoji]:
        """
        List with emojis on the guild.
        """
        return list(self._emojis)

    @property
    def roles(self) -> list[Role]:
        """
        List with roles on the guild.
        """
        return list(self._roles.values())

    @property
    def default_role(self) -> Role | None:
        """
        Guild default (@everyone) role.
        """
        return self._roles.get(self.id)

    @property
    def channels(self) -> list[Channel]:
        """
        A list with all the channels on the guild.
        """
        return list(self._channels.values())

    @property
    def text_channels(self) -> list[TextChannel]:
        """
        List with all text channels on the guild.
        """
        return list(filter(lambda c: isinstance(c, TextChannel), self.channels))  # type: ignore

    @property
    def voice_channels(self) -> list[VoiceChannel]:
        """
        List with all voice channels on the guild.
        """
        return list(filter(lambda c: isinstance(c, VoiceChannel), self.channels))  # type: ignore

    @property
    def category_channels(self) -> list[CategoryChannel]:
        """
        List of all category channels in the guild.
        """
        return list(filter(lambda c: isinstance(c, CategoryChannel), self.channels))  # type: ignore

    @property
    def members(self) -> list[GuildMember]:
        """
        List with members on the guild.
        """
        return list(self._members.values())

    @property
    def applications(self) -> list[Application]:
        """
        List with applications (bots) on the guild.
        """
        return list(self._applications.values())

    def get_application(self, application_id: int) -> Application | None:
        """
        Method to get application object by id.

        Parameters
        ----------
        application_id:
            Id of the application.
        """
        return self._applications.get(application_id)

    def get_role(self, role_id: int) -> Role | None:
        """
        Method to get a guild role by id.

        Parameters
        ----------
        role_id:
            Id of the role object.
        """
        return self._roles.get(role_id)

    def get_channel(self, channel_id: int) -> Channel | None:
        """
        Method to get a guild channel by id.

        Parameters
        ----------
        channel_id:
            Id of the channel object.
        """
        return self._channels.get(channel_id)

    def get_member(self, member_id: int) -> GuildMember | None:
        """
        Method to get a guild member by id.

        Parameters
        ----------
        member_id:
            Id of the member object.
        """
        return self._members.get(member_id)

    def get_voice_state(self, user: SelfBot) -> VoiceChannel | None:
        """
        Method to get selfbot voice state.

        Parameters
        ----------
        user:
            Selfbot to get voice state.
        """
        return user.get_voice_state(guild=self)

    async def fetch_ban(self, user: SelfBot, user_id: int) -> BanEntry:
        """
        Method to fetch guild ban.

        Parameters
        ----------
        user:
            Selfbot to send request.
        user_id:
            Id of banned user.

        Raises
        ------
        HTTPTimeoutError
            Request reached http timeout limit.
        HTTPException
            Fetching the ban failed.
        NotFound
            Banned user not found.
        Forbidden
            Selfbot doesn't have proper permissions.
        """
        data: dict[str, Any] = await user.http.fetch_guild_ban(
            user=user, guild_id=self.id, user_id=user_id
        )
        return BanEntry(state=self._state, data=data)

    async def fetch_bans(
        self, user: SelfBot, limit: int = 1000
    ) -> AsyncIterable[BanEntry]:
        """
        Method to fetch guild bans.

        Parameters
        ----------
        user:
            Selfbot to send request.
        limit:
            Maximum amount of fetched bans.

        Raises
        ------
        HTTPTimeoutError
            Request reached http timeout limit.
        HTTPException
            Fetching the bans failed.
        NotFound
            Banned user not found.
        Forbidden
            Selfbot doesn't have proper permissions.
        """
        for ban_data in await user.http.fetch_guild_bans(
            user=user, guild_id=self.id, limit=limit
        ):
            ban_data["guild_id"] = self.id
            yield BanEntry(state=self._state, data=ban_data)

    async def fetch_roles(self, user: SelfBot) -> list[Role]:
        """
        Method to fetch guild roles.

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
            Role not found.
        Forbidden
            Selfbot doesn't have proper permissions.
        """
        data: list[dict[str, Any]] = await self._state.http.fetch_guild_roles(
            user, guild_id=self.id
        )

        for role_data in data:
            role = Role(guild=self, data=role_data)

            self._roles[role.id] = role

        return list(self._roles.values())

    async def fetch_channel(self, user: SelfBot, channel_id: int) -> Channel:
        """
        Method to fetch guild channel.

        Parameters
        ----------
        user:
            Selfbot to send request.
        channel_id:
            Id of the channel.

        Raises
        ------
        HTTPTimeoutError
            Request reached http timeout limit.
        HTTPException
            Fetching the channel failed.
        NotFound
            Channel or Guild not found.
        Forbidden
            Selfbot doesn't have proper permissions.
        """
        data: dict[str, Any] = await self._state.http.fetch_channel(
            user, channel_id=channel_id
        )
        channel: Channel = self._state.create_guild_channel(guild=self, data=data)
        await channel.fetch_overwrites(user)

        self._add_channel(channel)
        return channel

    async def fetch_channels(self, user: SelfBot) -> list[Channel]:
        """
        Method to fetch guild channels.

        Parameters
        ----------
        user:
            Selfbot to send request.

        Raises
        ------
        HTTPTimeoutError
            Request reached http timeout limit.
        HTTPException
            Fetching the channels failed.
        NotFound
            Channel or Guild not found.
        Forbidden
            Selfbot doesn't have proper permissions.
        """
        channel_data: list[dict[str, Any]] = await self._state.http.fetch_channels(
            user, guild_id=self.id
        )

        for data in channel_data:
            channel: Channel = self._state.create_guild_channel(guild=self, data=data)
            await channel.fetch_overwrites(user)
            self._add_channel(channel)

        return self.channels

    async def fetch_member(self, user: SelfBot, member_id: int) -> GuildMember:
        """
        Method to fetch guild member.

        Parameters
        ----------
        user:
            Selfbot to send request.
        member_id:
            Id of the member.

        Raises
        ------
        HTTPTimeoutError
            Request reached http timeout limit.
        HTTPException
            Fetching the member failed.
        NotFound
            Member or Guild not found.
        Forbidden
            Selfbot doesn't have proper permissions.
        """
        data: dict[str, Any] = await self._state.http.fetch_member(
            user, guild_id=self.id, member_id=member_id
        )
        member: GuildMember = self._state.create_guild_member(data=data, guild=self)

        self._add_member(member)
        return member

    async def fetch_applications(self, user: SelfBot) -> list[Application]:
        """
        Method to fetch guild applications.

        Parameters
        ----------
        user:
            Selfbot to send request.

        Raises
        ------
        HTTPTimeoutError
            Request reached http timeout limit.
        HTTPException
            Fetching the applications failed.
        NotFound
            Guild not found.
        Forbidden
            Selfbot doesn't have proper permissions.
        """
        data: dict[str, Any] = await self._state.http.fetch_applications(
            user, guild_id=self.id
        )
        self._applications = {}

        for app_data in applications_filter(data).values():
            application: Application = self._state.create_application(app_data)
            self._add_application(application)

        return self.applications

    async def create_role(
        self,
        user: SelfBot,
        name: str | None = None,
        permissions: Permissions | None = None,
        color: Color | None = None,
        hoist: bool = False,
        mentionable: bool = False,
    ) -> Role:
        """
        Method to create role.

        Parameters
        ----------
        user:
            Selfbot to send request.
        name:
            Role name.
        permissions:
            Role permissions.
        color:
            Role color.
        hoist:
            Whether the role is pinned on the user list.
        mentionable:
            Whether this role is mentionable.

        Raises
        ------
        HTTPTimeoutError
            Request reached http timeout limit.
        HTTPException
            Creating the role failed.
        NotFound
            Guild not found.
        Forbidden
            Selfbot doesn't have proper permissions.
        """
        params: dict[str, Any] = {
            "name": name,
            "permissions": permissions.get_bitwise_by_flags() if permissions else None,
            "color": color.value if color else None,
            "hoist": hoist,
            "mentionable": mentionable,
        }

        data: dict[str, Any] = await self._state.http.create_role(
            user, guild_id=self.id, params=params
        )
        return Role(guild=self, data=data)

    async def create_text_channel(
        self,
        user: SelfBot,
        name: str,
        topic: str | None = None,
        parent: CategoryChannel | None = None,
        position: int | None = None,
        nsfw: bool = False,
        slowmode: int | None = None,
        overwrites: dict[GuildMember | Role, PermissionOverwrite] | None = None,
    ) -> TextChannel:
        """
        Method to create text channel.

        Parameters
        ----------
        user:
            Selfbot to send request.
        name:
            Channel name.
        topic:
            Channel topic.
        parent:
            Channel category.
        position:
            Position of the channel.
        nsfw:
            Whether the channel should be marked as nsfw.
        slowmode:
            Amount of seconds a user has to wait before sending another message.
            users with the permission manage_messages or manage_channel, are unaffected.
        overwrites:
            Channel overwrites.

        Raises
        ------
        HTTPTimeoutError
            Request reached http timeout limit.
        HTTPException
            Creating the channel failed.
        NotFound
            Guild not found.
        Forbidden
            Selfbot doesn't have proper permissions.
        """
        permission_overwrites: list[OverwritePayload] | None = None

        if overwrites is not None:
            permission_overwrites = self._state.to_overwrite_payload(overwrites)

        params: dict[str, Any] = {
            "name": name,
            "type": ChannelType.GUILD_TEXT.value,
            "topic": topic,
            "parent_id": parent.id if parent else None,
            "position": position,
            "nsfw": nsfw,
            "permission_overwrites": permission_overwrites,
            "rate_limit_per_user": slowmode,
        }

        data: dict[str, Any] = await self._state.http.create_channel(
            user=user, guild_id=self.id, params=params
        )
        channel = self._state.create_guild_channel(guild=self, data=data)
        assert isinstance(channel, TextChannel)

        return channel

    async def create_voice_channel(
        self,
        user: SelfBot,
        name: str,
        parent: CategoryChannel | None = None,
        position: int | None = None,
        nsfw: bool = False,
        slowmode: int | None = None,
        bitrate: int | None = None,
        user_limit: int = 0,
        video_quality_mode: int | None = None,
        overwrites: dict[GuildMember | Role, PermissionOverwrite] | None = None,
    ) -> VoiceChannel:
        """
        Method to create text channel.

        Parameters
        ----------
        user:
            Selfbot to send request.
        name:
        parent:
            Channel category.
        position:
            Position of the channel.
        nsfw:
            Whether the channel should be marked as nsfw.
        slowmode:
            Amount of seconds a user has to wait before sending another message.
            users with the permission manage_messages or manage_channel, are unaffected.
        bitrate:
            Voice channel bitrate.
        user_limit:
            Limit of users on the voice channel.
        video_quality_mode:
            Voice channel video quality mode.
        overwrites:
            Channel overwrites.

        Raises
        ------
        HTTPTimeoutError
            Request reached http timeout limit.
        HTTPException
            Creating the channel failed.
        NotFound
            Guild not found.
        Forbidden
            Selfbot doesn't have proper permissions.
        """
        permission_overwrites: list[OverwritePayload] | None = None

        if overwrites is not None:
            permission_overwrites = self._state.to_overwrite_payload(overwrites)

        params: dict[str, Any] = {
            "name": name,
            "type": ChannelType.GUILD_VOICE.value,
            "parent_id": parent.id if parent else None,
            "position": position,
            "nsfw": nsfw,
            "permission_overwrites": permission_overwrites,
            "rate_limit_per_user": slowmode,
            "user_limit": user_limit,
            "bitrate": bitrate,
            "video_quality_mode": video_quality_mode,
        }

        data: dict[str, Any] = await self._state.http.create_channel(
            user=user, guild_id=self.id, params=params
        )
        channel = self._state.create_guild_channel(guild=self, data=data)
        assert isinstance(channel, VoiceChannel)

        return channel

    async def create_category_channel(
        self,
        user: SelfBot,
        name: str,
        position: int | None = None,
        overwrites: dict[GuildMember | Role, PermissionOverwrite] | None = None,
    ) -> CategoryChannel:
        """
        Method to create text channel.

        Parameters
        ----------
        user:
            Selfbot to send request.
        name:
            Channel name.
        position:
            Position of the channel.
        overwrites:
            Channel overwrites.

        Raises
        ------
        HTTPTimeoutError
            Request reached http timeout limit.
        HTTPException
            Creating the channel failed.
        NotFound
            Guild not found.
        Forbidden
            Selfbot doesn't have proper permissions.
        """
        permission_overwrites: list[OverwritePayload] | None = None

        if overwrites is not None:
            permission_overwrites = self._state.to_overwrite_payload(overwrites)

        params: dict[str, Any] = {
            "name": name,
            "type": ChannelType.GUILD_CATEGORY.value,
            "position": position,
            "permission_overwrites": permission_overwrites,
        }

        data: dict[str, Any] = await self._state.http.create_channel(
            user=user, guild_id=self.id, params=params
        )
        channel = self._state.create_guild_channel(guild=self, data=data)

        assert isinstance(channel, CategoryChannel)
        return channel

    def _add_emoji(self, emoji: Emoji) -> None:
        self._emojis.add(emoji)

    def _remove_emoji(self, emoji: Emoji) -> None:
        try:
            self._emojis.remove(emoji)
        except KeyError:
            pass

    def _add_role(self, role: Role) -> None:
        self._roles[role.id] = role

    def _remove_role(self, role_id: int) -> None:
        try:
            del self._roles[role_id]
        except KeyError:
            pass

    def _add_channel(self, channel: Channel) -> None:
        self._channels[channel.id] = channel

    def _remove_channel(self, channel_id: int) -> None:
        try:
            del self._channels[channel_id]
        except KeyError:
            pass

    def _add_member(self, member: GuildMember) -> None:
        self._members[member.id] = member

    def _remove_member(self, member_id: int) -> None:
        try:
            del self._members[member_id]
        except KeyError:
            pass

    def _add_application(self, application: Application) -> None:
        self._applications[application.id] = application
