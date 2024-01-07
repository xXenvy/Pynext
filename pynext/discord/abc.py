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
from typing import TYPE_CHECKING, overload, Any, AsyncIterable

from asyncio import get_event_loop, AbstractEventLoop, Task, sleep

from .message import GuildMessage, PrivateMessage
from ..enums import PermissionsFlags
from ..errors import HTTPException

if TYPE_CHECKING:
    from .guild import Guild
    from .file import File

    from ..selfbot import SelfBot
    from ..state import State


class Typing:
    """
    Typing object used to send typing requests for the specified selfbots.

    Parameters
    ----------
    channel_id:
        Id of the channel.
    users:
        Tuple with selfbots.

    Attributes
    ----------
    users: :class:`tuple`
        Tuple with selfbots.
    channel_id: :class:`int`
        Id of the channel.
    """

    __slots__ = ("users", "channel_id", "_tasks", "_loop")

    def __init__(self, channel_id: int, users: tuple[SelfBot, ...]):
        self._tasks: list[Task] = []
        self._loop: AbstractEventLoop = get_event_loop()

        self.users: tuple[SelfBot, ...] = users
        self.channel_id: int = channel_id

    async def send_typing(self, user: SelfBot) -> None:
        """
        A method which starts a loop sending requests every 5 seconds for single selfbot.

        Parameters
        ----------
        user:
            Selfbot for which the loop should be run.
        """
        while True:
            await user.http.send_typing(user=user, channel_id=self.channel_id)
            await sleep(5)

    def __enter__(self) -> None:
        for user in self.users:
            self._tasks.append(self._loop.create_task(self.send_typing(user)))

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        for task in self._tasks:
            task.cancel()

    def __repr__(self) -> str:
        return f"<Typing(channel={self.channel_id}, users={len(self.users)})>"


class Messageable:
    __slots__ = ()

    if TYPE_CHECKING:
        _state: State
        id: int
        guild: Guild
        _messages: dict[int, GuildMessage | PrivateMessage]

    @property
    def messages(self) -> list[GuildMessage | PrivateMessage]:
        return list(self._messages.values())

    def typing(self, *users: SelfBot) -> Typing:
        return Typing(channel_id=self.id, users=users)

    @overload
    async def send(
        self, user: SelfBot, content: str, files: list[File] | None = None
    ) -> PrivateMessage:
        ...

    @overload
    async def send(
        self, user: SelfBot, content: str, files: list[File] | None = None
    ) -> GuildMessage:
        ...

    async def send(
        self, user: SelfBot, content: str, files: list[File] | None = None
    ) -> GuildMessage | PrivateMessage:
        attachments: list[dict[str, Any]] = []

        if files is not None:
            async for attachment_data in self._upload_files(user, files):
                attachments.append(attachment_data)

        message_data: dict[str, Any] = await self._state.http.send_message(
            user,
            channel_id=self.id,
            message_content=content,
            attachments=attachments or None,
        )

        if getattr(self, "guild", None):
            message_data["guild_id"] = self.guild.id

        message: GuildMessage | PrivateMessage | None = (
            await self._state.create_message_from_data(user=user, data=message_data)
        )
        if message is None:
            raise HTTPException(
                "Message not found. This is probably a library bug. Report it here: TODO"
            )

        message.channel._add_message(message)
        return message

    async def fetch_messages(
        self, user: SelfBot, limit: int = 10, message_id: int | None = None
    ) -> list[GuildMessage | PrivateMessage]:
        messages: list[GuildMessage | PrivateMessage] = []

        messages_data: list[dict[str, Any]] = await self._state.http.fetch_messages(
            user=user, channel_id=self.id, limit=limit, message_id=message_id
        )

        for message_data in messages_data:
            if getattr(self, "guild", None):
                message_data["guild_id"] = self.guild.id

            message: GuildMessage | PrivateMessage | None = (
                await self._state.create_message_from_data(user, message_data)
            )
            if message is not None:
                messages.append(message)

        for message in messages:
            self._add_message(message)

        return messages

    async def fetch_message(
        self, user: SelfBot, message_id: int
    ) -> GuildMessage | PrivateMessage:
        messages: list[GuildMessage | PrivateMessage] = await self.fetch_messages(
            user, limit=1, message_id=message_id
        )
        return messages[0]

    def get_message(self, message_id: int) -> GuildMessage | PrivateMessage | None:
        return self._messages.get(message_id)

    def _add_message(self, message: GuildMessage | PrivateMessage) -> None:
        self._messages[message.id] = message

    def _remove_message(self, message_id: int) -> None:
        try:
            del self._messages[message_id]
        except KeyError:
            pass

    async def _upload_files(
        self, user: SelfBot, files: list[File]
    ) -> AsyncIterable[dict[str, str | int]]:
        attachments_data: list[dict[str, Any]] = []

        for index, file in enumerate(files):
            attachments_data.append(
                {
                    "file_size": file.size,
                    "filename": file.name,
                    "id": str(index),
                }
            )

        response: dict[str, Any] = await self._state.http.upload_attachments(
            user=user, channel_id=self.id, files=attachments_data
        )

        for key, attachment in enumerate(response["attachments"]):
            upload_url: str = attachment["upload_url"]
            upload_id: int = attachment["id"]
            upload_filename: str = attachment["upload_filename"]

            file: File = files[key]

            await self._state.http.upload_file(upload_url, file.bytes)

            yield {
                "uploaded_filename": upload_filename,
                "filename": file.name,
                "id": upload_id,
            }


class BaseFlags:
    __slots__ = ()

    if TYPE_CHECKING:
        value: int

    @property
    def create_instant_invite(self) -> bool:
        flag_value: int = PermissionsFlags.CREATE_INSTANT_INVITE.value
        return (self.value & flag_value) == flag_value

    @create_instant_invite.setter
    def create_instant_invite(self, status: bool) -> None:
        flag_value: int = PermissionsFlags.CREATE_INSTANT_INVITE.value

        if self.create_instant_invite is False and status is True:
            self.value += flag_value

        elif self.create_instant_invite is True and status is False:
            self.value -= flag_value

    @property
    def kick_members(self) -> bool:
        flag: int = PermissionsFlags.KICK_MEMBERS.value
        return (self.value & flag) == flag

    @kick_members.setter
    def kick_members(self, status: bool) -> None:
        flag_value: int = PermissionsFlags.KICK_MEMBERS.value

        if self.kick_members is False and status is True:
            self.value += flag_value

        elif self.kick_members is True and status is False:
            self.value -= flag_value

    @property
    def ban_members(self) -> bool:
        flag: int = PermissionsFlags.BAN_MEMBERS.value
        return (self.value & flag) == flag

    @ban_members.setter
    def ban_members(self, status: bool) -> None:
        flag_value: int = PermissionsFlags.BAN_MEMBERS.value

        if self.ban_members is False and status is True:
            self.value += flag_value

        elif self.ban_members is True and status is False:
            self.value -= flag_value

    @property
    def administrator(self) -> bool:
        flag: int = PermissionsFlags.ADMINISTRATOR.value
        return (self.value & flag) == flag

    @administrator.setter
    def administrator(self, status: bool) -> None:
        flag_value: int = PermissionsFlags.ADMINISTRATOR.value

        if self.administrator is False and status is True:
            self.value += flag_value

        elif self.administrator is True and status is False:
            self.value -= flag_value

    @property
    def manage_channels(self) -> bool:
        flag: int = PermissionsFlags.MANAGE_CHANNELS.value

        return (self.value & flag) == flag

    @manage_channels.setter
    def manage_channels(self, status: bool) -> None:
        flag_value: int = PermissionsFlags.MANAGE_CHANNELS.value

        if self.manage_channels is False and status is True:
            self.value += flag_value

        elif self.manage_channels is True and status is False:
            self.value -= flag_value

    @property
    def manage_guild(self) -> bool:
        flag: int = PermissionsFlags.MANAGE_GUILD.value

        return (self.value & flag) == flag

    @manage_guild.setter
    def manage_guild(self, status: bool) -> None:
        flag_value: int = PermissionsFlags.MANAGE_GUILD.value

        if self.manage_guild is False and status is True:
            self.value += flag_value

        elif self.manage_guild is True and status is False:
            self.value -= flag_value

    @property
    def add_reactions(self) -> bool:
        flag: int = PermissionsFlags.ADD_REACTIONS.value

        return (self.value & flag) == flag

    @add_reactions.setter
    def add_reactions(self, status: bool) -> None:
        flag_value: int = PermissionsFlags.ADD_REACTIONS.value

        if self.add_reactions is False and status is True:
            self.value += flag_value

        elif self.add_reactions is True and status is False:
            self.value -= flag_value

    @property
    def view_audit_log(self) -> bool:
        flag: int = PermissionsFlags.VIEW_AUDIT_LOG.value

        return (self.value & flag) == flag

    @view_audit_log.setter
    def view_audit_log(self, status: bool) -> None:
        flag_value: int = PermissionsFlags.VIEW_AUDIT_LOG.value

        if self.view_audit_log is False and status is True:
            self.value += flag_value

        elif self.view_audit_log is True and status is False:
            self.value -= flag_value

    @property
    def priority_speaker(self) -> bool:
        flag: int = PermissionsFlags.PRIORITY_SPEAKER.value

        return (self.value & flag) == flag

    @priority_speaker.setter
    def priority_speaker(self, status: bool) -> None:
        flag_value: int = PermissionsFlags.PRIORITY_SPEAKER.value

        if self.priority_speaker is False and status is True:
            self.value += flag_value

        elif self.priority_speaker is True and status is False:
            self.value -= flag_value

    @property
    def stream(self) -> bool:
        flag: int = PermissionsFlags.STREAM.value

        return (self.value & flag) == flag

    @stream.setter
    def stream(self, status: bool) -> None:
        flag_value: int = PermissionsFlags.STREAM.value

        if self.stream is False and status is True:
            self.value += flag_value

        elif self.stream is True and status is False:
            self.value -= flag_value

    @property
    def view_channel(self) -> bool:
        flag: int = PermissionsFlags.VIEW_CHANNEL.value

        return (self.value & flag) == flag

    @view_channel.setter
    def view_channel(self, status: bool) -> None:
        flag_value: int = PermissionsFlags.VIEW_CHANNEL.value

        if self.view_channel is False and status is True:
            self.value += flag_value

        elif self.view_channel is True and status is False:
            self.value -= flag_value

    @property
    def send_messages(self) -> bool:
        flag: int = PermissionsFlags.SEND_MESSAGES.value

        return (self.value & flag) == flag

    @send_messages.setter
    def send_messages(self, status: bool) -> None:
        flag_value: int = PermissionsFlags.SEND_MESSAGES.value

        if self.send_messages is False and status is True:
            self.value += flag_value

        elif self.send_messages is True and status is False:
            self.value -= flag_value

    @property
    def send_tts_messages(self) -> bool:
        flag: int = PermissionsFlags.SEND_TTS_MESSAGES.value

        return (self.value & flag) == flag

    @send_tts_messages.setter
    def send_tts_messages(self, status: bool) -> None:
        flag_value: int = PermissionsFlags.SEND_TTS_MESSAGES.value

        if self.send_tts_messages is False and status is True:
            self.value += flag_value

        elif self.send_tts_messages is True and status is False:
            self.value -= flag_value

    @property
    def manage_messages(self) -> bool:
        flag: int = PermissionsFlags.MANAGE_MESSAGES.value

        return (self.value & flag) == flag

    @manage_messages.setter
    def manage_messages(self, status: bool) -> None:
        flag_value: int = PermissionsFlags.MANAGE_MESSAGES.value

        if self.manage_channels is False and status is True:
            self.value += flag_value

        elif self.manage_channels is True and status is False:
            self.value -= flag_value

    @property
    def embed_links(self) -> bool:
        flag: int = PermissionsFlags.EMBED_LINKS.value

        return (self.value & flag) == flag

    @embed_links.setter
    def embed_links(self, status: bool) -> None:
        flag_value: int = PermissionsFlags.EMBED_LINKS.value

        if self.embed_links is False and status is True:
            self.value += flag_value

        elif self.embed_links is True and status is False:
            self.value -= flag_value

    @property
    def attach_files(self) -> bool:
        flag: int = PermissionsFlags.ATTACH_FILES.value

        return (self.value & flag) == flag

    @attach_files.setter
    def attach_files(self, status: bool) -> None:
        flag_value: int = PermissionsFlags.ATTACH_FILES.value

        if self.attach_files is False and status is True:
            self.value += flag_value

        elif self.attach_files is True and status is False:
            self.value -= flag_value

    @property
    def read_message_history(self) -> bool:
        flag: int = PermissionsFlags.READ_MESSAGE_HISTORY.value

        return (self.value & flag) == flag

    @read_message_history.setter
    def read_message_history(self, status: bool) -> None:
        flag_value: int = PermissionsFlags.READ_MESSAGE_HISTORY.value

        if self.read_message_history is False and status is True:
            self.value += flag_value

        elif self.read_message_history is True and status is False:
            self.value -= flag_value

    @property
    def mention_everyone(self) -> bool:
        flag: int = PermissionsFlags.MENTION_EVERYONE.value

        return (self.value & flag) == flag

    @mention_everyone.setter
    def mention_everyone(self, status: bool) -> None:
        flag_value: int = PermissionsFlags.MENTION_EVERYONE.value

        if self.mention_everyone is False and status is True:
            self.value += flag_value

        elif self.mention_everyone is True and status is False:
            self.value -= flag_value

    @property
    def use_external_emojis(self) -> bool:
        flag: int = PermissionsFlags.USE_EXTERNAL_EMOJIS.value

        return (self.value & flag) == flag

    @use_external_emojis.setter
    def use_external_emojis(self, status: bool) -> None:
        flag_value: int = PermissionsFlags.USE_EXTERNAL_EMOJIS.value

        if self.use_external_emojis is False and status is True:
            self.value += flag_value

        elif self.use_external_emojis is True and status is False:
            self.value -= flag_value

    @property
    def view_guild_insights(self) -> bool:
        flag: int = PermissionsFlags.VIEW_GUILD_INSIGHTS.value

        return (self.value & flag) == flag

    @view_guild_insights.setter
    def view_guild_insights(self, status: bool) -> None:
        flag_value: int = PermissionsFlags.VIEW_GUILD_INSIGHTS.value

        if self.view_guild_insights is False and status is True:
            self.value += flag_value

        elif self.view_guild_insights is True and status is False:
            self.value -= flag_value

    @property
    def connect(self) -> bool:
        flag: int = PermissionsFlags.CONNECT.value

        return (self.value & flag) == flag

    @connect.setter
    def connect(self, status: bool) -> None:
        flag_value: int = PermissionsFlags.CONNECT.value

        if self.connect is False and status is True:
            self.value += flag_value

        elif self.connect is True and status is False:
            self.value -= flag_value

    @property
    def speak(self) -> bool:
        flag: int = PermissionsFlags.SPEAK.value

        return (self.value & flag) == flag

    @speak.setter
    def speak(self, status: bool) -> None:
        flag_value: int = PermissionsFlags.SPEAK.value

        if self.speak is False and status is True:
            self.value += flag_value

        elif self.speak is True and status is False:
            self.value -= flag_value

    @property
    def mute_members(self) -> bool:
        flag: int = PermissionsFlags.MUTE_MEMBERS.value

        return (self.value & flag) == flag

    @mute_members.setter
    def mute_members(self, status: bool) -> None:
        flag_value: int = PermissionsFlags.MUTE_MEMBERS.value

        if self.mute_members is False and status is True:
            self.value += flag_value

        elif self.mute_members is True and status is False:
            self.value -= flag_value

    @property
    def deafen_members(self) -> bool:
        flag: int = PermissionsFlags.DEAFEN_MEMBERS.value

        return (self.value & flag) == flag

    @deafen_members.setter
    def deafen_members(self, status: bool) -> None:
        flag_value: int = PermissionsFlags.DEAFEN_MEMBERS.value

        if self.deafen_members is False and status is True:
            self.value += flag_value

        elif self.deafen_members is True and status is False:
            self.value -= flag_value

    @property
    def move_members(self) -> bool:
        flag: int = PermissionsFlags.MOVE_MEMBERS.value

        return (self.value & flag) == flag

    @move_members.setter
    def move_members(self, status: bool) -> None:
        flag_value: int = PermissionsFlags.MOVE_MEMBERS.value

        if self.move_members is False and status is True:
            self.value += flag_value

        elif self.move_members is True and status is False:
            self.value -= flag_value

    @property
    def change_nickname(self) -> bool:
        flag: int = PermissionsFlags.CHANGE_NICKNAME.value

        return (self.value & flag) == flag

    @change_nickname.setter
    def change_nickname(self, status: bool) -> None:
        flag_value: int = PermissionsFlags.CHANGE_NICKNAME.value

        if self.change_nickname is False and status is True:
            self.value += flag_value

        elif self.change_nickname is True and status is False:
            self.value -= flag_value

    @property
    def manage_nicknames(self) -> bool:
        flag: int = PermissionsFlags.MANAGE_NICKNAMES.value

        return (self.value & flag) == flag

    @manage_nicknames.setter
    def manage_nicknames(self, status: bool) -> None:
        flag_value: int = PermissionsFlags.MANAGE_NICKNAMES.value

        if self.manage_nicknames is False and status is True:
            self.value += flag_value

        elif self.manage_nicknames is True and status is False:
            self.value -= flag_value

    @property
    def manage_roles(self) -> bool:
        flag: int = PermissionsFlags.MANAGE_ROLES.value

        return (self.value & flag) == flag

    @manage_roles.setter
    def manage_roles(self, status: bool) -> None:
        flag_value: int = PermissionsFlags.MANAGE_ROLES.value

        if self.manage_roles is False and status is True:
            self.value += flag_value

        elif self.manage_roles is True and status is False:
            self.value -= flag_value

    @property
    def manage_webhooks(self) -> bool:
        flag: int = PermissionsFlags.MANAGE_WEBHOOKS.value

        return (self.value & flag) == flag

    @manage_webhooks.setter
    def manage_webhooks(self, status: bool) -> None:
        flag_value: int = PermissionsFlags.MANAGE_WEBHOOKS.value

        if self.manage_webhooks is False and status is True:
            self.value += flag_value

        elif self.manage_webhooks is True and status is False:
            self.value -= flag_value

    @property
    def manage_threads(self) -> bool:
        flag: int = PermissionsFlags.MANAGE_THREADS.value

        return (self.value & flag) == flag

    @manage_threads.setter
    def manage_threads(self, status: bool) -> None:
        flag_value: int = PermissionsFlags.MANAGE_THREADS.value

        if self.manage_threads is False and status is True:
            self.value += flag_value

        elif self.manage_threads is True and status is False:
            self.value -= flag_value

    @property
    def create_public_threads(self) -> bool:
        flag: int = PermissionsFlags.CREATE_PUBLIC_THREADS.value

        return (self.value & flag) == flag

    @create_public_threads.setter
    def create_public_threads(self, status: bool) -> None:
        flag_value: int = PermissionsFlags.CREATE_PUBLIC_THREADS.value

        if self.create_public_threads is False and status is True:
            self.value += flag_value

        elif self.create_public_threads is True and status is False:
            self.value -= flag_value

    @property
    def create_private_threads(self) -> bool:
        flag: int = PermissionsFlags.CREATE_PRIVATE_THREADS.value

        return (self.value & flag) == flag

    @create_private_threads.setter
    def create_private_threads(self, status: bool) -> None:
        flag_value: int = PermissionsFlags.CREATE_PRIVATE_THREADS.value

        if self.create_private_threads is False and status is True:
            self.value += flag_value

        elif self.create_private_threads is True and status is False:
            self.value -= flag_value

    @property
    def moderate_members(self) -> bool:
        flag: int = PermissionsFlags.MODERATE_MEMBERS.value

        return (self.value & flag) == flag

    @moderate_members.setter
    def moderate_members(self, status: bool) -> None:
        flag_value: int = PermissionsFlags.MODERATE_MEMBERS.value

        if self.moderate_members is False and status is True:
            self.value += flag_value

        elif self.moderate_members is True and status is False:
            self.value -= flag_value
