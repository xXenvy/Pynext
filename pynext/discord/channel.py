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

from ..utils import Hashable, snowflake_time, str_to_datetime
from ..types import OverwritePayload
from ..errors import WebsocketNotConnected, VoiceStateNotFound
from ..enums import ChannelType

from .abc import Messageable
from .permissions import PermissionOverwrite
from .message import GuildMessage
from .discorduser import DiscordUser

if TYPE_CHECKING:
    from datetime import datetime

    from ..state import State
    from ..selfbot import SelfBot

    from .guild import Guild
    from .member import GuildMember
    from .message import PrivateMessage
    from .role import Role


class BaseChannel(Hashable):
    """
    BaseChannel implementation.

    Parameters
    ----------
    state:
        State object.
    data:
        Channel data.

    Attributes
    ----------
    raw_data:
        Channel raw data.
    id:
        id of the channel.
    """

    __slots__ = (
        "id",
        "raw_data",
        "_state",
    )

    def __init__(self, state: State, data: dict[str, Any]):
        self._state: State = state

        self.raw_data: dict[str, Any] = data
        self.id: int = int(data["id"])

    def __repr__(self) -> str:
        return f"<BaseChannel(id={self.id})>"

    @property
    def created_at(self) -> datetime:
        """
        Datetime object of when the channel was created.
        """
        return snowflake_time(self.id)


class DMChannel(BaseChannel, Messageable):
    """
    DMchannel representation. Related to a specific user.

    Parameters
    ----------
    state:
        State object.
    data:
        Channel data.

    Attributes
    ----------
    raw_data: :class:`dict`
        Channel raw data.
    target: :class:`DiscordUser`
        Related to channel discord user.
    id: :class:`int`
        Channel id.
    last_message_id: Optional[:class:`int`]
        last message id. If any.
    """

    __slots__ = ("target", "_messages", "last_message_id")

    def __init__(self, state: State, data: dict[str, Any]):
        super().__init__(state=state, data=data)

        author_data: dict[str, str | int] = data["recipients"][0]
        self.target: DiscordUser = self._state.create_user(data=author_data)

        if last_message_id := data.get("last_message_id"):
            self.last_message_id: int | None = int(last_message_id)
        else:
            self.last_message_id: int | None = None

        self._messages: dict[int, PrivateMessage] = {}

    def __repr__(self) -> str:
        return f"<DMChannel(id={self.id})>"


class GuildChannel(BaseChannel):
    """
    GuildChannel representation.

    Parameters
    ----------
    state:
        State object.
    guild:
        Guild on which the channel is.
    data:
        Channel data.

    Attributes
    ----------
    raw_data: :class:`dict`
        Channel raw data.
    guild: :class:`Guild`
        Guild on which the channel is.
    name: :class:`str`
        Channel name.
    id: :class:`int`
        Id of the channel.
    position: :class:`int`
        Channel position on the guild.
    flags: :class:`int`
        Channel flags.
    type: :class:`int`
        Channel type.
    parent_id: :class:`int`
        Channel category id.
    """

    __slots__ = (
        "guild",
        "name",
        "position",
        "flags",
        "type",
        "parent_id",
        "_overwrites",
    )

    def __init__(self, state: State, guild: Guild, data: dict[str, Any]):
        super().__init__(state=state, data=data)

        self.guild = guild
        self.name: str = self.raw_data["name"]

        self.position: int = self.raw_data["flags"]
        self.flags: int = self.raw_data["flags"]
        self.type: int = self.raw_data["type"]

        self.parent_id: int | None = self.raw_data.get("parent_id")
        if self.parent_id is not None:
            self.parent_id = int(self.parent_id)

        self._overwrites: dict[GuildMember | Role, PermissionOverwrite] = {}

    def __repr__(self) -> str:
        return f"<GuildChannel(name={self.name}, id={self.id}, type={self.type})>"

    @property
    def parent(self) -> CategoryChannel | TextChannel | GuildChannel | None:
        """
        Channel category. For ThreadChannel it's TextChannel.

        .. note::
            It can also be GuildChannel, since we do not support forum channels yet.
        """
        if self.parent_id is None:
            return None

        channel = self.guild.get_channel(self.parent_id)
        if channel is not None:
            assert isinstance(channel, (TextChannel, CategoryChannel, GuildChannel))

        return channel

    @property
    def overwrites(self) -> dict[GuildMember | Role, PermissionOverwrite]:
        """
        Channel overwrites.
        """
        return self._overwrites

    async def fetch_overwrites(
        self, user: SelfBot
    ) -> dict[GuildMember | Role, PermissionOverwrite]:
        """
        Method to fetch channel overwrites.

        Parameters
        ----------
        user:
            Selfbot required to send requests.
        """
        overwrites = self.raw_data.get("permission_overwrites", [])
        async for overwrite, target in self._state.create_overwrites(
            user, self.guild, overwrites
        ):
            self._add_overwrite(target=target, overwrite=overwrite)

        return self.overwrites

    async def delete(self, user: SelfBot) -> None:
        """
        Method to delete channel.

        Parameters
        ----------
        user:
            Selfbot required to send request.

        Raises
        ------
        HTTPTimeoutError
            Request reached http timeout limit.
        HTTPException
            Deleting the channel failed.
        NotFound
            Channel not found.
        Forbidden
            Selfbot doesn't have proper permissions.
        """
        await self._state.http.delete_channel(user, channel_id=self.id)

    def _add_overwrite(
        self, target: GuildMember | Role, overwrite: PermissionOverwrite
    ) -> None:
        self._overwrites[target] = overwrite


class CategoryChannel(GuildChannel):
    """
    CategoryChannel. A variation of the guild channel.

    Parameters
    ----------
    state:
        State object.
    data:
        Channel data.
    guild:
        Guild on which the channel is located.

    Attributes
    ----------
    raw_data: :class:`dict`
        Channel raw data.
    guild: :class:`Guild`
        Guild on which the channel is.
    name: :class:`str`
        Channel name.
    id: :class:`int`
        Id of the channel.
    position: :class:`int`
        Channel position on the guild.
    flags: :class:`int`
        Channel flags.
    type: :class:`int`
        Channel type.
    parent_id: :class:`int`
        Channel category id.
    """

    __slots__ = ()

    def __init__(self, state: State, guild: Guild, data: dict[str, Any]):
        super().__init__(state, guild, data)

    def __repr__(self):
        return f"<CategoryChannel(name={self.name}, id={self.id})>"

    async def edit(
        self,
        user: SelfBot,
        name: str | None = None,
        position: int | None = None,
        overwrites: dict[GuildMember | Role, PermissionOverwrite] | None = None,
    ) -> CategoryChannel:
        """
        Method to edit category channel.

        Parameters
        ----------
        user:
            Selfbot required to send requests.
        name:
            New channel name.
        position:
            New channel position.
        overwrites:
            New channel overwrites.

        Raises
        ------
        HTTPTimeoutError
            Request reached http timeout limit.
        HTTPException
            Editing the channel failed.
        NotFound
            Channel not found.
        Forbidden
            Selfbot doesn't have proper permissions.
        """
        if not name and not position and not overwrites:
            # If person did not provide any new parameters.
            return self

        permission_overwrites: list[OverwritePayload] | None = None

        if overwrites is not None:
            permission_overwrites = self._state.to_overwrite_payload(overwrites)

        params: dict[str, Any] = {
            "name": name,
            "type": ChannelType.GUILD_CATEGORY.value,
            "position": position,
            "permission_overwrites": permission_overwrites,
        }

        for key, value in params.copy().items():
            if value is None:
                """
                If a parameter has a value of None,
                we don't want it in the dict because it could overwrite an already set parameter.
                """
                del params[key]

        data: dict[str, Any] = await self._state.http.edit_channel(
            user, channel_id=self.id, params=params
        )
        channel = self._state.create_guild_channel(guild=self.guild, data=data)

        assert isinstance(channel, CategoryChannel)
        return channel


class TextChannel(GuildChannel, Messageable):
    """
    TextChannel. A variation of the guild channel.

    Parameters
    ----------
    state:
        State object.
    data:
        Channel data.
    guild:
        Guild on which the channel is located.

    Attributes
    ----------
    raw_data: :class:`dict`
        Channel raw data.
    guild: :class:`Guild`
        Guild on which the channel is.
    name: :class:`str`
        Channel name.
    id: :class:`int`
        Id of the channel.
    position: :class:`int`
        Channel position on the guild.
    flags: :class:`int`
        Channel flags.
    type: :class:`int`
        Channel type.
    parent_id: :class:`int`
        Channel category id.
    last_message_id: Optional[:class:`int`]
        last message id. If any.
    topic: :class:`str`
        Channel topic.
    nsfw: :class:`bool`
        Whether the channel has nsfw feature enabled.
    """

    __slots__ = ("topic", "nsfw", "last_message_id", "_messages", "_threads")

    def __init__(self, state: State, guild: Guild, data: dict[str, Any]):
        super().__init__(state, guild, data)

        self.topic: str | None = self.raw_data.get("nsfw")
        self.nsfw: bool = self.raw_data.get("nsfw", False)
        if last_message_id := data.get("last_message_id"):
            self.last_message_id: int | None = int(last_message_id)
        else:
            self.last_message_id: int | None = None

        self._messages: dict[int, GuildMessage] = {}
        self._threads: dict[int, ThreadChannel] = {}

    def __repr__(self):
        return f"<TextChannel(name={self.name}, id={self.id})>"

    @property
    def threads(self) -> list[ThreadChannel]:
        """
        List with cached threads on the channel.

        .. versionadded:: 1.2.0
        """
        return list(self._threads.values())

    async def edit(
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
        Method to edit category channel.

        Parameters
        ----------
        user:
            Selfbot required to send requests.
        name:
            New channel name.
        topic:
            New channel topic.
        parent:
            New channel parent.
        position:
            New channel position.
        nsfw:
            Whether the channel should have nsfw option enabled.
        slowmode:
            New channel slowmode.
        overwrites:
            New channel overwrites.

        Raises
        ------
        HTTPTimeoutError
            Request reached http timeout limit.
        HTTPException
            Editing the channel failed.
        NotFound
            Channel not found.
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

        for key, value in params.copy().items():
            if value is None:
                """
                If a parameter has a value of None,
                we don't want it in the dict because it could overwrite an already set parameter.
                """
                del params[key]

        data: dict[str, Any] = await self._state.http.edit_channel(
            user, channel_id=self.id, params=params
        )

        channel = self._state.create_guild_channel(guild=self.guild, data=data)
        assert isinstance(channel, TextChannel)
        return channel

    def get_thread(self, message_id: int) -> ThreadChannel | None:
        """
        Method to get Thread by message id.

        Parameters
        ----------
        message_id:
            Id of the message that started the thread.

        .. versionadded:: 1.2.0
        """
        return self._threads.get(message_id)

    def _add_thread(self, thread: ThreadChannel) -> None:
        self._threads[thread.id] = thread

    def _remove_thread(self, message_id: int) -> None:
        try:
            del self._threads[message_id]
        except KeyError:
            pass


class VoiceChannel(GuildChannel):
    """
    VoiceChannel. A variation of the guild channel.

    Parameters
    ----------
    state:
        State object.
    data:
        Channel data.
    guild:
        Guild on which the channel is located.

    Attributes
    ----------
    raw_data: :class:`dict`
        Channel raw data.
    guild: :class:`Guild`
        Guild on which the channel is.
    name: :class:`str`
        Channel name.
    id: :class:`int`
        Id of the channel.
    position: :class:`int`
        Channel position on the guild.
    flags: :class:`int`
        Channel flags.
    type: :class:`int`
        Channel type.
    parent_id: :class:`int`
        Channel category id.
    user_limit: Optional[:class:`int`]
        Limit of users on the voice channel.
    bitrate: :class:`int`
        Voice channel bitrate.
    """

    __slots__ = ("user_limit", "bitrate")

    def __init__(self, state: State, guild: Guild, data: dict[str, Any]):
        super().__init__(state, guild, data)

        self.user_limit: int | None = self.raw_data["user_limit"]
        if self.user_limit == 0:
            self.user_limit = None

        self.bitrate: int = self.raw_data["bitrate"]

    def __repr__(self):
        return f"<VoiceChannel(name={self.name}, id={self.id})>"

    async def connect(
        self, user: SelfBot, self_mute: bool = False, self_deaf: bool = False
    ) -> None:
        """
        Method to connect selfbot to voice channel.

        Parameters
        ----------
        user:
            Selfbot to connect the channel.
        self_mute:
            Whether the selfbot should mute their microphone.
        self_deaf:
            Whether selfbot should have a muted sound.

        Raises
        ------
        WebsocketNotConnected
            SelfBot has no connection to the gateway.
        """
        if not user.gateway:
            raise WebsocketNotConnected(
                f"SelfBot: {user} has no connection to the gateway."
            )

        await user.gateway.change_voice_state(
            guild_id=self.guild.id,
            channel_id=self.id,
            self_mute=self_mute,
            self_deaf=self_deaf,
        )

        user._update_voice_state(guild=self.guild, state=self)

    async def disconnect(self, user: SelfBot) -> None:
        """
        Method to disconnect selfbot from voice channel.

        Parameters
        ----------
        user:
            Selfbot to disconnect from channel.

        Raises
        ------
        WebsocketNotConnected
            SelfBot has no connection to the gateway.
        VoiceStateNotFound
            SelfBot is not connected to any channel on the guild.
        """
        if not user.gateway:
            raise WebsocketNotConnected(
                f"SelfBot: {user} has no connection to the gateway."
            )

        if user.get_voice_state(guild=self.guild) is None:
            raise VoiceStateNotFound(
                "SelfBot is not connected to any channel on the guild."
            )

        await user.gateway.change_voice_state(guild_id=self.guild.id, channel_id=None)

        user._update_voice_state(guild=self.guild, state=None)

    async def edit(
        self,
        user: SelfBot,
        name: str,
        parent: CategoryChannel | None = None,
        position: int | None = None,
        nsfw: bool = False,
        slowmode: int | None = None,
        bitrate: int | None = None,
        user_limit: int | None = None,
        video_quality_mode: int | None = None,
        overwrites: dict[GuildMember | Role, PermissionOverwrite] | None = None,
    ) -> VoiceChannel:
        """
        Method to edit voice channel.

        Parameters
        ----------
        user:
            Selfbot required to send requests.
        name:
            New channel name.
        parent:
            New channel parent.
        position:
            New channel position.
        nsfw:
            Whether the channel should have nsfw option enabled.
        slowmode:
            New channel slowmode.
        user_limit:
            limit of users on the voice channel.
        bitrate:
            New voice channel bitrate.
        video_quality_mode:
            New voice channel video quality mode.
        overwrites:
            New channel overwrites.

        Raises
        ------
        HTTPTimeoutError
            Request reached http timeout limit.
        HTTPException
            Editing the channel failed.
        NotFound
            Channel not found.
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
            "permission_overwrite": permission_overwrites,
            "rate_limit_per_user": slowmode,
            "user_limit": user_limit,
            "bitrate": bitrate,
            "video_quality_mode": video_quality_mode,
        }

        for key, value in params.copy().items():
            if value is None:
                """
                If a parameter has a value of None,
                we don't want it in the dict because it could overwrite an already set parameter.
                """
                del params[key]

        data: dict[str, Any] = await self._state.http.edit_channel(
            user=user, channel_id=self.id, params=params
        )
        channel = self._state.create_guild_channel(guild=self.guild, data=data)
        assert isinstance(channel, VoiceChannel)

        return channel


class ThreadChannel(GuildChannel, Messageable):
    """
    ThreadChannel. A variation of the guild channel.

    Parameters
    ----------
    state:
        State object.
    data:
        Channel data.
    guild:
        Guild on which the channel is located.

    Attributes
    ----------
    raw_data: :class:`dict`
        Channel raw data.
    guild: :class:`Guild`
        Guild on which the channel is.
    name: :class:`str`
        Channel name.
    id: :class:`int`
        Id of the channel.
    position: :class:`int`
        Channel position on the guild.
    flags: :class:`int`
        Channel flags.
    type: :class:`int`
        Channel type.
    parent_id: :class:`int`
        Channel category id.
    archive_timestamp: :class:`datetime.datetime`
        When the thread was archived.
    create_timestamp: :class:`datetime.datetime`
        When the thread was created.
    archived: :class:`bool`
        Whether the thread is archived.
    auto_archive_duration: :class:`int`
        Duration in minutes to automatically archive the thread after recent activity.
    locked: :class:`bool`
        Whether the thread is locked.
    total_message_sent: Optional[:class:`int`]
        Total message sent in the thread.
    member_count: :class:`int`
        Total members in the thread.
    owner_id: :class:`int`
        Id of the thread owner.
    last_message_id: Optional[:class:`int`]
        Id of the last message sent in the thread.
    """

    __slots__ = (
        "archive_timestamp",
        "create_timestamp",
        "archived",
        "auto_archive_duration",
        "locked",
        "total_message_sent",
        "member_count",
        "owner_id",
        "last_message_id",
        "_messages",
        "_members",
    )

    def __init__(self, state: State, guild: Guild, data: dict[str, Any]):
        super().__init__(state, guild, data)

        meta: dict[str, Any] = data["thread_metadata"]

        self.archive_timestamp: datetime = str_to_datetime(meta["archive_timestamp"])
        self.create_timestamp: datetime = str_to_datetime(meta["create_timestamp"])

        self.archived: bool = meta["archived"]
        self.auto_archive_duration: int = meta["auto_archive_duration"]
        self.locked: bool = meta["locked"]

        self.total_message_sent: int | None = data.get("total_message_sent")
        self.member_count: int = data["member_count"]
        self.owner_id: int = int(data["owner_id"])

        if last_message_id := data.get("last_message_id"):
            self.last_message_id: int | None = int(last_message_id)
        else:
            self.last_message_id: int | None = None

        self._messages: dict[int, GuildMessage] = {}
        self._members: dict[int, GuildMember] = {}

    def __repr__(self) -> str:
        return f"<ThreadChannel(name={self.name}, id={self.id})>"

    @property
    def members(self) -> list[GuildMember]:
        """
        A list with thread members.
        """
        return list(self._members.values())

    @property
    def owner(self) -> GuildMember | None:
        """
        A Member who created the thread. If cached.
        """
        return self.guild.get_member(self.owner_id)

    @property
    def creation_message_id(self) -> int:
        """
        Id of the creation message.
        """
        return self.id

    @property
    def creation_message(self) -> GuildMessage | None:
        """
        Creaction message object if cached.
        """
        if not isinstance(self.parent, TextChannel):
            return None

        message = self.parent.get_message(self.id)
        if isinstance(message, GuildMessage):
            return message

    def get_member(self, member_id: int) -> GuildMember | None:
        """
        Method to get thread member by id.
        """
        return self._members.get(member_id)

    async def edit(
        self, user: SelfBot, name: str | None = None, slowmode: int | None = None
    ) -> ThreadChannel:
        """
        Method to edit thread channel.

        Parameters
        ----------
        user:
            Selfbot required to send request.
        name:
            New channel name.
        slowmode:
            New channel slowmode.

        Raises
        ------
        HTTPTimeoutError
            Request reached http timeout limit.
        HTTPException
            Editing the channel failed.
        NotFound
            Channel not found.
        Forbidden
            Selfbot doesn't have proper permissions.
        """
        if name is None and slowmode is None:
            # If person did not provide any new parameters.
            # We don't want to send a request.
            return self

        params: dict[str, Any] = {
            "name": name,
            "type": ChannelType.PUBLIC_THREAD.value,
            "rate_limit_per_user": slowmode,
        }

        for key, value in params.copy().items():
            if value is None:
                """
                If a parameter has a value of None,
                we don't want it in the dict because it could overwrite an already set parameter.
                """
                del params[key]

        data: dict[str, Any] = await self._state.http.edit_channel(
            user=user, channel_id=self.id, params=params
        )
        channel = self._state.create_guild_channel(guild=self.guild, data=data)
        assert isinstance(channel, ThreadChannel)

        return channel

    def _add_member(self, member: GuildMember) -> None:
        self._members[member.id] = member

    def _remove_member(self, member_id: int) -> None:
        try:
            del self._members[member_id]
        except KeyError:
            pass
