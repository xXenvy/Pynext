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
from enum import Enum


class ChannelType(Enum):
    DM = 1
    GUILD_TEXT = 0
    GUILD_VOICE = 2
    GUILD_CATEGORY = 4
    GUILD_FORUM = 15
    PUBLIC_THREAD = 11
    PRIVATE_THREAD = 12
    GUILD_ANNOUNCEMENT = 5


class VideoQuality(Enum):
    AUTO = 1
    FULL = 2


class PermissionsFlags(Enum):
    CREATE_INSTANT_INVITE = 1 << 0
    KICK_MEMBERS = 1 << 1
    BAN_MEMBERS = 1 << 2
    ADMINISTRATOR = 1 << 3
    MANAGE_CHANNELS = 1 << 4
    MANAGE_GUILD = 1 << 5
    ADD_REACTIONS = 1 << 6
    VIEW_AUDIT_LOG = 1 << 7
    PRIORITY_SPEAKER = 1 << 8
    STREAM = 1 << 9
    VIEW_CHANNEL = 1 << 10
    SEND_MESSAGES = 1 << 11
    SEND_TTS_MESSAGES = 1 << 12
    MANAGE_MESSAGES = 1 << 13
    EMBED_LINKS = 1 << 14
    ATTACH_FILES = 1 << 15
    READ_MESSAGE_HISTORY = 1 << 16
    MENTION_EVERYONE = 1 << 17
    USE_EXTERNAL_EMOJIS = 1 << 18
    VIEW_GUILD_INSIGHTS = 1 << 19
    CONNECT = 1 << 20
    SPEAK = 1 << 21
    MUTE_MEMBERS = 1 << 22
    DEAFEN_MEMBERS = 1 << 23
    MOVE_MEMBERS = 1 << 24
    CHANGE_NICKNAME = 1 << 26
    MANAGE_NICKNAMES = 1 << 27
    MANAGE_ROLES = 1 << 28
    MANAGE_WEBHOOKS = 1 << 29
    MANAGE_THREADS = 1 << 34
    CREATE_PUBLIC_THREADS = 1 << 35
    CREATE_PRIVATE_THREADS = 1 << 36
    MODERATE_MEMBERS = 1 << 40


class GatewayCodes(Enum):
    DISPATCH = 0
    HEARTBEAT = 1
    IDENTIFY = 2
    PRESENCE = 3
    VOICE_STATE = 4
    VOICE_PING = 5
    RESUME = 6
    RECONNECT = 7
    REQUEST_MEMBERS = 8
    INVALIDATE_SESSION = 9
    HELLO = 10
    HEARTBEAT_ACK = 11
    GUILD_SYNC = 12


class Events(Enum):
    READY = "on_user_ready"

    CHANNEL_DELETE = "on_channel_delete"
    CHANNEL_CREATE = "on_channel_create"
    CHANNEL_UPDATE = "on_channel_edit"

    MESSAGE_CREATE = "on_message_create"
    MESSAGE_DELETE = "on_message_delete"
    MESSAGE_UPDATE = "on_message_edit"

    MESSAGE_REACTION_REMOVE = "on_message_reaction_remove"
    MESSAGE_REACTION_ADD = "on_message_reaction_add"

    GUILD_CREATE = "on_guild_create"
    GUILD_UPDATE = "on_guild_update"
    GUILD_DELETE = "on_guild_delete"

    GUILD_EMOJIS_UPDATE = "on_guild_emojis_update"
    GUILD_MEMBER_UPDATE = "on_member_update"

    GUILD_BAN_ADD = "on_guild_ban_create"
    GUILD_BAN_REMOVE = "on_guild_ban_remove"

    GUILD_ROLE_CREATE = "on_guild_role_create"
    GUILD_ROLE_UPDATE = "on_guild_role_update"
    GUILD_ROLE_DELETE = "on_guild_role_delete"

    INTERACTION_CREATE = "on_interaction_create"
    INTERACTION_SUCCESS = "on_interaction_success"
    INTERACTION_FAILURE = "on_interaction_failure"


class DefaultAvatar(Enum):
    blurple = 0
    grey = 1
    gray = 1
    green = 2
    orange = 3
    red = 4
    fuchsia = 5
    pink = 5

    def __str__(self) -> str:
        return self.name


class StatusType(Enum):
    ONLINE = "online"
    DND = "dnd"
    IDLE = "idle"
    INVISIBLE = "invisible"
    OFFLINE = "offline"


class ActivityType(Enum):
    GAME = 0
    STREAMING = 1
    LISTENING = 2
    WATCHING = 3
    COMPETING = 5


class CommandOptionType(Enum):
    STRING = 3
    INTEGER = 4
    BOOLEAN = 5
    USER = 6
    CHANNEL = 7
    ROLE = 8
    NUMBER = 10
