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
from .discord import *
from .types import *
from .client import *
from .selfbot import *
from .errors import *
from .enums import *
from .gateway import *

__all__: tuple[str, ...] = (
    "__version__",
    "PynextClient",
    "SelfBot",
    "GuildMessage",
    "GuildMember",
    "Guild",
    "Role",
    "TextChannel",
    "VoiceChannel",
    "GuildChannel",
    "CategoryChannel",
    "ChannelType",
    "Color",
    "MessageReaction",
    "Permissions",
    "PermissionsFlags",
    "PermissionOverwrite",
    "Emoji",
    "OverwritePayload",
    "Authorization",
    "MessageReference",
    "PynextError",
    "HTTPException",
    "Forbidden",
    "FunctionIsNotCoroutine",
    "VoiceStateNotFound",
    "NotFound",
    "WebsocketNotConnected",
    "Unauthorized",
    "Image",
    "CaptchaRequired",
    "PresenceBuilder",
    "StatusType",
    "ActivityType",
    "Activity",
    "Message",
    "DMChannel",
    "PrivateMessage",
    "DiscordUser",
    "EmojisUpdatePayload",
    "VideoQuality",
    "RatelimitPayload",
    "BadRequest",
    "BanEntry",
    "Dispatcher",
    "GatewayResponse",
    "HTTPTimeoutError",
    "Messageable",
    "Typing",
    "Application",
    "SlashCommand",
    "SubCommand",
    "CommandOptionType",
    "UnSupportedOptionType",
    "ApplicationCommandOption",
    "InteractionPayload",
    "Attachment",
    "ThreadChannel",
    "ThreadMembersUpdatePayload",
    "File",
    "BaseMessage",
    "BaseCommand",
)

__version__: str = PynextClient.__version__
