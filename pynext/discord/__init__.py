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

from .message import *
from .guild import *
from .channel import *
from .role import *
from .member import *
from .color import *
from .reaction import *
from .permissions import *
from .image import *
from .discorduser import *
from .presence import *
from .activity import *
from .banentry import *
from .abc import *
from .emoji import *
from .application import *
from .slash_command import *
from .attachment import *
from .file import *

__all__ = (
    "GuildMessage",
    "Guild",
    "VoiceChannel",
    "TextChannel",
    "Role",
    "DMChannel",
    "GuildChannel",
    "GuildMember",
    "CategoryChannel",
    "Image",
    "PrivateMessage",
    "Color",
    "MessageReaction",
    "Emoji",
    "Permissions",
    "PermissionOverwrite",
    "DiscordUser",
    "PresenceBuilder",
    "Activity",
    "BanEntry",
    "Messageable",
    "Typing",
    "Application",
    "SlashCommand",
    "SubCommand",
    "Attachment",
    "ThreadChannel",
    "File",
    "BaseMessage",
    "BaseCommand",
)
