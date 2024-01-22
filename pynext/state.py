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
from typing import TYPE_CHECKING, AsyncIterable, Any, TypeVar

from logging import Logger, getLogger

from .discord import *
from .errors import HTTPException, Forbidden, Unauthorized
from .enums import ChannelType
from .types import OverwritePayload

if TYPE_CHECKING:
    from .rest import HTTPClient
    from .selfbot import SelfBot
    from .types import Channel, Message

MessageT = TypeVar("MessageT", GuildMessage, PrivateMessage)


class State:
    """
    State is the provider between the HTTP client.
    It creates objects through data received from the HTTP response.

    Parameters
    ----------
    http:
        HTTPClient to send requests, that are needed to create some objects.

    Attributes
    ----------
    http: :class:`HTTPClient`
        Global HTTPClient object.
    logger: :class:`logging.Logger`
        State logger.
    """

    __slots__ = ("http", "logger")

    def __init__(self, http: HTTPClient) -> None:
        self.http: HTTPClient = http
        self.logger: Logger = getLogger("pynext.common")

    def create_private_message(self, data: dict[str, Any]) -> PrivateMessage:
        """
        Method to create a private message object from a data.

        Parameters
        ----------
        data:
            Required data to create a message object.
        """
        self.logger.debug("Creating a private message object...")
        return PrivateMessage(state=self, message_data=data)

    def create_guild_message(self, data: dict[str, Any]) -> GuildMessage:
        """
        Method to create a guild message object from a data.

        Parameters
        ----------
        data:
            Required data to create a message object.
        """
        self.logger.debug("Creating a guild message object...")
        return GuildMessage(state=self, message_data=data)

    def create_guild_channel(self, guild: Guild, data: dict[str, Any]) -> Channel:
        """
        Method to create a guild channel object from a data.

        Parameters
        ----------
        guild:
            Guild to which the created channel should belong.
        data:
            Required data to create a channel object.
        """
        self.logger.debug("Creating a guild channel object...")
        return self.guild_channel_factory(
            GuildChannel(state=self, guild=guild, data=data)
        )

    def create_dm_channel(self, data: dict[str, Any]) -> DMChannel:
        """
        Method to create a dm channel object from a data.

        Parameters
        ----------
        data:
            Required data to create a channel object.
        """
        self.logger.debug("Creating a dm channel object...")
        return DMChannel(state=self, data=data)

    def create_user(self, data: dict[str, Any]) -> DiscordUser:
        """
        Method to create a discord user object from a data.

        Parameters
        ----------
        data:
            Required data to create a user object.
        """
        self.logger.debug("Creating a discord user object...")
        return DiscordUser(state=self, user_data=data)

    def create_guild_member(self, guild: Guild, data: dict[str, Any]) -> GuildMember:
        """
        Method to create a guild member object from a data.

        Parameters
        ----------
        guild:
            Guild to which the created member should belong.
        data:
            Required data to create a member object.
        """
        self.logger.debug("Creating a guild member object...")
        return GuildMember(data=data, guild=guild)

    @staticmethod
    def create_button(message: Message | BaseMessage, row: int, data: dict[str, Any]) -> Button:
        """
        Method to create a button object from a data.

        .. versionadded:: 1.3.0

        Parameters
        ----------
        message:
            Message to which the created button should belong.
        row:
            Row number of the button.
        data:
            Required data to create a button object.
        """
        return Button(message=message, row=row, data=data)

    @staticmethod
    def create_select_menu(message: Message | BaseMessage, row: int, data: dict[str, Any]) -> SelectMenu:
        """
        Method to create a select menu object from a data.

        .. versionadded:: 1.3.0

        Parameters
        ----------
        message:
            Message to which the created select menu should belong.
        row:
            Row number of the select menu.
        data:
            Required data to create a select menu object.
        """
        return SelectMenu(message=message, row=row, data=data)

    def create_attachment(
        self, message: MessageT, data: dict[str, Any]
    ) -> Attachment[MessageT]:
        """
        Method to create a attachment object from a data.

        .. versionadded:: 1.2.0

        Parameters
        ----------
        message:
            Message to which the created attachment should belong.
        data:
            Required data to create a attachment object.
        """
        self.logger.debug("Creating a attachment object...")
        return Attachment(data=data, message=message)

    def create_application(self, data: dict[str, Any]) -> Application:
        """
        Method to create a application object from a data.

        .. versionadded:: 1.0.8

        Parameters
        ----------
        data:
            Required data to create a application object.
        """
        self.logger.debug("Creating a application object...")
        return Application(state=self, data=data)

    def create_slash_command(
        self, application: Application, data: dict[str, Any]
    ) -> SlashCommand:
        """
        Method to create a SlashCommand object from a data.

        .. versionadded:: 1.0.8

        Parameters
        ----------
        application:
            Application to which the command is assigned.
        data:
            Required data to create a SlashCommand object.
        """
        self.logger.debug("Creating a SlashCommand object...")
        return SlashCommand(application, data)

    def create_sub_command(
        self, parent: SlashCommand | SubCommand, data: dict[str, Any]
    ) -> SubCommand:
        """
        Method to create a SubCommand object from a data.

        .. versionadded:: 1.0.8

        Parameters
        ----------
        parent:
            SlashCommand / SubCommand to which the subcommand is assigned.
        data:
            Required data to create a SubCommand object.
        """
        self.logger.debug("Creating a SubCommand object...")
        data["id"] = parent.id
        data["version"] = parent.version_id
        return SubCommand(parent, data)

    async def create_message_from_data(
        self, user: SelfBot, data: dict[str, Any]
    ) -> PrivateMessage | GuildMessage | None:
        """
        Method to create a message object from data.

        Parameters
        ----------
        user:
            Selfbot, which will make requests needed to create message.
        data:
            Required data to create a message object.
        """
        self.logger.debug("Creating a message object...")

        channel_id: int = int(data["channel_id"])

        if guild_id := data.get("guild_id"):
            guild_id: int | None = int(guild_id)
        elif guild_id := data.get("message_reference", {}).get("guild_id"):
            guild_id: int | None = int(guild_id)
        else:
            guild_id: int | None = None

        if guild_id is None:
            author_id: int = int(data["author"]["id"])

            author: DiscordUser | None = user.get_user(user_id=author_id)
            if not author:
                author = await user.fetch_user(author_id)

            dm_channel: DMChannel | None = user.get_dm_channel(channel_id=channel_id)

            if not isinstance(dm_channel, DMChannel):
                dm_channel = await user.fetch_dm_channel(channel_id=channel_id)

            data["channel"] = dm_channel
            data["user_author"] = author

            return self.create_private_message(data=data)

        if data["type"] == 21:
            channel_id = int(data["message_reference"]["channel_id"])

        guild: Guild | None = user.get_guild(guild_id)
        if not guild:
            guild = await user.fetch_guild(guild_id)

        channel = guild.get_channel(channel_id=channel_id)

        if not isinstance(channel, (TextChannel, ThreadChannel)):
            try:
                channel = await guild.fetch_channel(user=user, channel_id=channel_id)
            except (Forbidden, HTTPException, Unauthorized):
                return

        if isinstance(channel, TextChannel) and data["type"] == 21:
            thread_id: int = int(data["channel_id"])

            channel = channel.get_thread(thread_id)
            if channel is None:
                channel = await guild.fetch_channel(user=user, channel_id=thread_id)

        data["guild"] = guild
        data["channel"] = channel
        data["user_author"] = self.create_guild_member(guild=guild, data=data["author"])
        return self.create_guild_message(data=data)

    async def create_guild(
        self, user: SelfBot, guild_data: dict[str, Any], chunk_channels: bool = True
    ) -> Guild:
        """
        Method to create a guild object from data.

        Parameters
        ----------
        user:
            Selfbot, which will make requests needed to create guild.
        guild_data:
            Required data to create a guild object.
        chunk_channels:
            Whether to chunk channels after guild build.
        """
        self.logger.debug("Creating a guild object...")
        if guild_data.get("properties"):
            guild_data = {**guild_data, **guild_data["properties"]}

        guild: Guild = Guild(state=self, data=guild_data)

        if chunk_channels:
            await self.chunk_guild_channels(
                user=user, guild=guild, data=guild_data.get("channels", [])
            )

        await self.fetch_guild_owner(guild=guild, user=user)

        return guild

    async def chunk_guild_channels(
        self, user: SelfBot, guild: Guild, data: list[dict[str, Any]]
    ) -> None:
        """
        Method to chunk guild channels.

        Parameters
        ----------
        user:
            Selfbot, which will make requests needed to chunk channels.
        guild:
            Guild to which the chucked channels belong.
        data:
            Required data to create a channels.
        """
        for channel_data in data:
            channel = self.guild_channel_factory(
                GuildChannel(state=self, guild=guild, data=channel_data)
            )
            await channel.fetch_overwrites(user)
            guild._add_channel(channel)

    @staticmethod
    async def fetch_guild_owner(guild: Guild, user: SelfBot) -> None:
        """
        Method to fetch guild owner.

        Parameters
        ----------
        guild:
            Guild of the owner we want to fetch.
        user:
            Selfbot, which will make requests to fetch owner.
        """
        if guild.owner:
            return

        await guild.fetch_member(user, guild.owner_id)

    @staticmethod
    def to_overwrite_payload(
        overwrites: dict[GuildMember | Role, PermissionOverwrite]
    ) -> list[OverwritePayload]:
        """
        Method to convert overwrites to list with overwrite payload.

        Parameters
        ----------
        overwrites:
            Overwrites to convert.
        """
        permission_overwrites: list[OverwritePayload] = []
        for target, overwrite in overwrites.items():
            permission_overwrites.append(
                OverwritePayload(
                    id=target.id,
                    type=0 if isinstance(target, Role) else 1,
                    allow=str(overwrite.allow.value),
                    deny=str(overwrite.deny.value),
                )
            )

        return permission_overwrites

    def guild_channel_factory(self, channel: GuildChannel) -> Channel:
        """
        Method that converts a GuldChannel object to a specific channel type object.

        .. warning::
            Method can return GuildChannel once again if we do not yet support the specified channel type.

        Parameters
        ----------
        channel:
            Base GuildChannel object.
        """

        if channel.type == ChannelType.GUILD_VOICE.value:
            return VoiceChannel(state=self, guild=channel.guild, data=channel.raw_data)
        if channel.type == ChannelType.GUILD_CATEGORY.value:
            return CategoryChannel(
                state=self, guild=channel.guild, data=channel.raw_data
            )
        if channel.type == ChannelType.GUILD_TEXT.value:
            return TextChannel(state=self, guild=channel.guild, data=channel.raw_data)
        if channel.type in (
            ChannelType.PUBLIC_THREAD.value,
            ChannelType.PRIVATE_THREAD.value,
        ):
            return ThreadChannel(state=self, guild=channel.guild, data=channel.raw_data)

        return channel

    @staticmethod
    async def create_overwrites(
        user: SelfBot, guild: Guild, overwrites_data: list[dict[str, Any]]
    ) -> AsyncIterable[tuple[PermissionOverwrite, Role | GuildMember]]:
        """
        Method that creates overwrites from data.

        Parameters
        ----------
        user:
            Selfbot that will make requests to fetch a role or guild member.
        guild:
            Guild to which PermissionOverwrite belongs.
        overwrites_data:
            list with overwrite data.
        """

        for data in overwrites_data:
            if int(data["type"]) == 0:
                role: Role | None = guild.get_role(int(data["id"]))
                if role is None:
                    continue

                overwrite: PermissionOverwrite = PermissionOverwrite.make_from_value(
                    allow=int(data["allow"]), deny=int(data["deny"])
                )
                yield overwrite, role

            else:
                member: GuildMember | None = guild.get_member(member_id=int(data["id"]))

                if member is None:
                    try:
                        member = await guild.fetch_member(
                            user, member_id=int(data["id"])
                        )
                    except (Forbidden, HTTPException, Unauthorized):
                        continue

                if member is None:
                    continue

                overwrite: PermissionOverwrite = PermissionOverwrite.make_from_value(
                    allow=int(data["allow"]), deny=int(data["deny"])
                )

                yield overwrite, member

    async def fetch_channel_parent(
        self, channel: Channel, user: SelfBot
    ) -> CategoryChannel | None:
        """
        Method which fetches the channel parent.

        Parameters
        ----------
        channel:
            Channel to fetch parent.
        user:
            Selfbot that will make requests to category channel.
        """
        parent_id: int | None = channel.parent_id

        if parent_id is None or channel.guild is None:
            return None

        category = channel.guild.get_channel(parent_id)
        if isinstance(category, CategoryChannel):
            return category

        channel_data: dict[str, Any] = await self.http.fetch_channel(
            user, channel_id=parent_id
        )
        channel = self.create_guild_channel(guild=channel.guild, data=channel_data)

        if channel is not None:
            assert isinstance(channel, CategoryChannel)

        return channel

    @staticmethod
    async def fetch_message_from_raw(
        user: SelfBot, guild_id: int | None, channel_id: int, message_id: int
    ) -> Message | None:
        """
        Method that fetches a message without Guild and Channel objects.

        Parameters
        ----------
        user:
            Selfbot that will make requests.
        guild_id:
            The id of the guild to which the message was sent.
            If it is None, it means that the message is on the DM channel.
        channel_id:
            Id of the channel on which the message is sended.
        message_id:
            Specify message id.
        """

        if guild_id:
            guild: Guild | None = user.get_guild(guild_id)

            if not guild:
                guild = await user.fetch_guild(guild_id=guild_id)

            channel = guild.get_channel(channel_id)
            if not isinstance(channel, TextChannel):
                channel = await guild.fetch_channel(user, channel_id=channel_id)

            if not isinstance(channel, TextChannel):
                return

            message: Message | None = channel.get_message(message_id)
            if not message:
                return

            return message
        else:
            dm_channel: DMChannel | None = user.get_dm_channel(channel_id=channel_id)
            if not dm_channel:
                dm_channel = await user.fetch_dm_channel(channel_id=channel_id)

            dm_message = dm_channel.get_message(message_id)
            if not dm_message:
                return

            return dm_message
