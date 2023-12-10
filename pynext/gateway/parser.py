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
from typing import TYPE_CHECKING, Any, Callable, Coroutine

from asyncio import AbstractEventLoop, get_event_loop

from ..discord import *
from ..errors import Forbidden
from ..types import Message, Channel, EmojisUpdatePayload, InteractionPayload

if TYPE_CHECKING:
    from ..selfbot import SelfBot
    from .response import GatewayResponse


class Parser:
    """
    Parser is responsible for parsing arguments passed to events.

    Parameters
    ----------
    chunk_guilds:
        Whether the client should chunk guilds of each selfbot.
    chunk_channels:
        Whether the client should chunks guild channels.

    Attributes
    ----------
    chunk_guilds: :class:`bool`
        Whether the client should chunk guilds of each selfbot.
    chunk_channels: :class:`bool`
        Whether the client should chunks guild channels.
    loop: :class:`asyncio.AbstractEventLoop`
        Client loop.
    """

    __slots__ = ("chunk_guilds", "chunk_channels", "loop")

    def __init__(self, chunk_guilds: bool, chunk_channels: bool):
        self.chunk_guilds: bool = chunk_guilds
        self.chunk_channels: bool = chunk_channels

        self.loop: AbstractEventLoop = get_event_loop()

    async def parse_event_args(
        self, response: GatewayResponse
    ) -> tuple[Any, ...] | None:
        if response.event_name is not None:
            flag_args: Callable[[GatewayResponse], Coroutine] | None = getattr(
                self, response.event_name + "_args", None
            )

            if not flag_args:
                return

            return await flag_args(response)

    async def on_user_ready_args(self, response: GatewayResponse) -> tuple[SelfBot]:
        await self._chunk_user(response.user, data=response.data)
        response.user._ready.set()
        return (response.user,)

    @staticmethod
    async def on_message_create_args(
        response: GatewayResponse,
    ) -> tuple[SelfBot, Message] | None:
        message: Message | None = await response.user.state.create_message_from_data(
            response.user, response.data
        )
        if message and isinstance(message.channel, (TextChannel, DMChannel, ThreadChannel)):
            message.channel._add_message(message)
            return response.user, message

    @staticmethod
    async def on_message_edit_args(
        response: GatewayResponse,
    ) -> tuple[SelfBot, Message, Message] | None:
        message: Message | None = await response.user.state.create_message_from_data(
            response.user, response.data
        )

        if message is None:
            return

        old_message: Message | None = message.channel.get_message(message.id)
        message.channel._add_message(message)

        if old_message is None:
            return

        return response.user, old_message, message

    @staticmethod
    async def on_message_delete_args(
        response: GatewayResponse,
    ) -> tuple[SelfBot, Message] | None:
        try:
            guild_id: int | None = int(response.data["guild_id"])
        except KeyError:
            guild_id = None

        channel_id: int = int(response.data["channel_id"])
        message_id: int = int(response.data["id"])

        message: Message | None = await response.user.state.fetch_message_from_raw(
            user=response.user,
            guild_id=guild_id,
            channel_id=channel_id,
            message_id=message_id,
        )

        if message:
            message.channel._remove_message(message_id)
            return response.user, message

    @staticmethod
    async def on_channel_create_args(
        response: GatewayResponse,
    ) -> tuple[SelfBot, Channel | DMChannel]:
        data: dict[str, Any] = response.data
        user: SelfBot = response.user

        if data.get("guild_id"):
            guild_id: int = int(data["guild_id"])
            guild: Guild | None = user.get_guild(guild_id)

            if guild is None:
                guild = await user.fetch_guild(guild_id)

            channel: Channel = user.state.create_guild_channel(guild=guild, data=data)
            guild._add_channel(channel)
            return user, channel
        else:
            dm_channel: DMChannel = user.state.create_dm_channel(data=response.data)
            user._add_dm_channel(channel=dm_channel)
            return user, dm_channel

    @staticmethod
    async def on_channel_edit_args(
        response: GatewayResponse,
    ) -> tuple[SelfBot, Channel, Channel] | None:
        data: dict[str, Any] = response.data
        user: SelfBot = response.user

        if data.get("guild_id"):
            guild_id: int = int(data["guild_id"])
            guild: Guild | None = user.get_guild(guild_id)
            channel_id: int = int(data["id"])

            if guild is None:
                guild = await user.fetch_guild(guild_id)

            channel: Channel = user.state.create_guild_channel(guild=guild, data=data)
            await channel.fetch_overwrites(user)

            try:
                await user.state.fetch_channel_parent(channel, user)
            except Forbidden:
                pass

            old_channel: Channel | None = guild.get_channel(channel_id)
            guild._add_channel(channel)
            if old_channel:
                return user, old_channel, channel

    async def on_channel_delete_args(
        self, response: GatewayResponse
    ) -> tuple[SelfBot, Channel] | None:
        data: dict[str, Any] = response.data
        user: SelfBot = response.user

        if data.get("guild_id"):
            channel_id: int = int(data["id"])
            guild_id: int = int(data["guild_id"])
            guild: Guild | None = user.get_guild(guild_id)

            if guild is None:
                self.loop.create_task(user.fetch_guild(guild_id))
                return

            channel: Channel | None = guild.get_channel(channel_id)
            guild._remove_channel(channel_id)
            if channel:
                return user, channel

    @staticmethod
    async def on_guild_create_args(response: GatewayResponse) -> tuple[SelfBot, Guild]:
        data: dict[str, Any] = response.data
        user: SelfBot = response.user

        guild: Guild = await user.state.create_guild(user=user, guild_data=data)
        user._add_guild(guild)
        return user, guild

    async def on_guild_update_args(
        self, response: GatewayResponse
    ) -> tuple[SelfBot, Guild, Guild] | None:
        data: dict[str, Any] = response.data
        user: SelfBot = response.user

        guild_id: int = int(data["id"])
        old_guild: Guild | None = user.get_guild(guild_id)

        data["channels"] = await user.http.fetch_channels(user=user, guild_id=guild_id)
        new_guild: Guild = await self.chunk_user_guild(
            user=user, guild_data=data, fetch_only=True
        )

        if old_guild:
            return user, old_guild, new_guild

    async def on_guild_emojis_update_args(
        self, response: GatewayResponse
    ) -> tuple[SelfBot, EmojisUpdatePayload] | None:
        data: dict[str, Any] = response.data
        user: SelfBot = response.user

        guild_id: int = int(data["guild_id"])
        guild: Guild | None = user.get_guild(guild_id)

        if guild is None:
            self.loop.create_task(user.fetch_guild(guild_id))
            return

        updated_emojis: list[Emoji] = [
            Emoji(
                name=emoji_data["name"],
                animated=emoji_data["animated"],
                emoji_id=emoji_data["id"],
            )
            for emoji_data in data["emojis"]
        ]

        added_emojis: list[Emoji] = []
        removed_emojis: list[Emoji] = []

        for guild_emoji in guild.emojis:
            if guild_emoji not in updated_emojis:
                guild._remove_emoji(guild_emoji)
                removed_emojis.append(guild_emoji)

        for updated_emoji in updated_emojis:
            if updated_emoji not in guild.emojis:
                guild._add_emoji(updated_emoji)
                added_emojis.append(updated_emoji)

        return user, EmojisUpdatePayload(
            guild, added_emojis=added_emojis, deleted_emojis=removed_emojis
        )

    @staticmethod
    async def on_member_update_args(
        response: GatewayResponse,
    ) -> tuple[SelfBot, GuildMember, GuildMember] | None:
        data: dict[str, Any] = response.data
        user: SelfBot = response.user

        guild_id: int = int(data["guild_id"])
        guild: Guild | None = user.get_guild(guild_id)

        if guild is None:
            guild = await user.fetch_guild(guild_id)
            member: GuildMember = user.state.create_guild_member(guild=guild, data=data)
            guild._add_member(member)
            return

        new_member: GuildMember = user.state.create_guild_member(guild=guild, data=data)
        old_member: GuildMember | None = guild.get_member(new_member.id)
        guild._add_member(new_member)

        if old_member:
            return user, old_member, new_member

    @staticmethod
    async def on_guild_delete_args(
        response: GatewayResponse,
    ) -> tuple[SelfBot, Guild] | None:
        data: dict[str, Any] = response.data
        user: SelfBot = response.user

        guild_id: int = int(data["id"])
        guild: Guild | None = user.get_guild(guild_id)

        if guild:
            user._remove_guild(guild.id)
            return user, guild

    @staticmethod
    async def on_guild_ban_create_args(
        response: GatewayResponse,
    ) -> tuple[SelfBot, BanEntry]:
        data: dict[str, Any] = response.data
        user: SelfBot = response.user

        ban_entry: BanEntry = BanEntry(state=user.state, data=data)
        guild: Guild | None = user.get_guild(ban_entry.guild_id)

        if guild:
            guild._remove_member(ban_entry.user.id)  # type: ignore
            # Im not sure why pyright gets an error here, strange.

        return user, ban_entry

    @staticmethod
    async def on_guild_ban_remove_args(
        response: GatewayResponse,
    ) -> tuple[SelfBot, BanEntry]:
        data: dict[str, Any] = response.data
        user: SelfBot = response.user

        return user, BanEntry(state=user.state, data=data)

    @staticmethod
    async def on_guild_role_create_args(
        response: GatewayResponse,
    ) -> tuple[SelfBot, Role]:
        data: dict[str, Any] = response.data
        user: SelfBot = response.user

        role_data: dict[str, Any] = data["role"]
        guild_id: int = int(data["guild_id"])

        guild: Guild | None = user.get_guild(guild_id)

        if guild is None:
            guild = await user.fetch_guild(guild_id)

        role: Role = Role(guild=guild, data=role_data)
        guild._add_role(role)

        return user, role

    async def on_guild_role_update_args(
        self, response: GatewayResponse
    ) -> tuple[SelfBot, Role, Role] | None:
        data: dict[str, Any] = response.data
        user: SelfBot = response.user

        role_data: dict[str, Any] = data["role"]
        guild_id: int = int(data["guild_id"])

        guild: Guild | None = user.get_guild(guild_id)

        if guild is None:
            self.loop.create_task(user.fetch_guild(guild_id))
            return

        old_role: Role | None = guild.get_role(role_id=int(role_data["id"]))

        new_role: Role = Role(guild=guild, data=role_data)
        guild._add_role(new_role)

        if not old_role:
            return

        return user, old_role, new_role

    async def on_guild_role_delete_args(
        self, response: GatewayResponse
    ) -> tuple[SelfBot, Role] | None:
        data: dict[str, Any] = response.data
        user: SelfBot = response.user

        guild_id: int = int(data["guild_id"])
        role_id: int = int(data["role_id"])

        guild: Guild | None = user.get_guild(guild_id=guild_id)
        if guild is None:
            self.loop.create_task(user.fetch_guild(guild_id))
            return

        role: Role | None = guild.get_role(role_id=role_id)
        if not role:
            return

        return user, role

    @staticmethod
    async def on_message_reaction_add_args(
        response: GatewayResponse,
    ) -> tuple[SelfBot, MessageReaction] | None:
        try:
            guild_id: int | None = int(response.data["guild_id"])
        except KeyError:
            guild_id = None

        channel_id: int = int(response.data["channel_id"])
        message_id: int = int(response.data["message_id"])

        message: Message | None = await response.user.state.fetch_message_from_raw(
            user=response.user,
            guild_id=guild_id,
            channel_id=channel_id,
            message_id=message_id,
        )

        if message:
            reaction: MessageReaction = MessageReaction(
                message=message, data=response.data
            )
            message._add_reaction(reaction)
            return response.user, reaction

    @staticmethod
    async def on_message_reaction_remove_args(
        response: GatewayResponse,
    ) -> tuple[SelfBot, MessageReaction] | None:
        try:
            guild_id: int | None = int(response.data["guild_id"])
        except KeyError:
            guild_id = None

        channel_id: int = int(response.data["channel_id"])
        message_id: int = int(response.data["message_id"])

        message: Message | None = await response.user.state.fetch_message_from_raw(
            user=response.user,
            guild_id=guild_id,
            channel_id=channel_id,
            message_id=message_id,
        )
        if message:
            message_reaction: MessageReaction = MessageReaction(
                message=message, data=response.data
            )
            message._remove_reaction(message_reaction)
            return response.user, message_reaction

    @staticmethod
    async def on_interaction_create_args(
        response: GatewayResponse,
    ) -> tuple[SelfBot, InteractionPayload]:
        data: dict[str, Any] = response.data
        return response.user, InteractionPayload(int(data["nonce"]), int(data["id"]))

    @staticmethod
    async def on_interaction_success_args(
        response: GatewayResponse,
    ) -> tuple[SelfBot, InteractionPayload]:
        data: dict[str, Any] = response.data
        return response.user, InteractionPayload(int(data["nonce"]), int(data["id"]))

    @staticmethod
    async def on_interaction_failure_args(
        response: GatewayResponse,
    ) -> tuple[SelfBot, InteractionPayload]:
        data: dict[str, Any] = response.data
        return response.user, InteractionPayload(int(data["nonce"]), int(data["id"]))

    async def chunk_user_guild(
        self, user: SelfBot, guild_data: dict[str, Any], fetch_only: bool = False
    ) -> Guild:
        guild: Guild | None = None

        if fetch_only is False:
            guild = user.get_guild(guild_id=int(guild_data["id"]))

        if not guild:
            guild = await user.state.create_guild(
                user=user, guild_data=guild_data, chunk_channels=self.chunk_channels
            )

        user._add_guild(guild)
        return guild

    async def _chunk_user(self, user: SelfBot, data: dict[str, Any]):
        if self.chunk_guilds:
            for guild_data in data["guilds"]:
                await self.chunk_user_guild(user, guild_data=guild_data)

        for user_data in data["users"]:
            discord_user = user.state.create_user(data=user_data)
            user._add_user(discord_user)
