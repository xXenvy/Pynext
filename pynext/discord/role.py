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

from datetime import datetime

from ..utils import Hashable, snowflake_time
from .permissions import Permissions
from .color import Color

if TYPE_CHECKING:
    from ..selfbot import SelfBot
    from .guild import Guild


class Role(Hashable):
    """
    Representation of the guild role object.

    Discord docs: https://discord.com/developers/docs/topics/permissions#role-object

    Parameters
    ----------
    guild:
        Guild on which the role is located.
    data:
        Role data.

    Attributes
    ----------
    guild:
        Guild on which the role is located.
    permissions:
        Role permissions object.
    id:
        Role id.
    name:
        Role name.
    managed:
        Whether this role is managed by an integration.
    position:
        Position of this role.
    hoist:
        If this role is pinned in the user listing.
    mentionable:
        Whether this role is mentionable.
    color:
        Role color.
    """

    __slots__ = (
        "id",
        "name",
        "managed",
        "position",
        "hoist",
        "mentionable",
        "guild",
        "color",
        "permissions",
    )

    def __init__(self, guild: Guild, data: dict[str, Any]):
        self.guild: Guild = guild
        self.permissions: Permissions = Permissions(value=int(data["permissions"]))

        self.id: int = int(data["id"])
        self.name: str = data["name"]
        self.managed: bool = data["managed"]

        self.position: int = data["position"]
        self.hoist: bool = data["hoist"]
        self.mentionable: bool = data["mentionable"]
        self.color: Color = Color(data["color"])

    def __repr__(self) -> str:
        return f"<Role(name={self.name}, id={self.id})>"

    @property
    def created_at(self) -> datetime:
        """
        Datetime object of when the role was created.
        """
        return snowflake_time(self.id)

    @property
    def mention(self) -> str:
        """
        Role mention format.
        """
        if self.is_default() is False:
            return f"<@&{self.id}>"

        return "@everyone"

    def is_default(self) -> bool:
        """
        Method to check if role is default (@everyone).
        """
        return self.guild.id == self.id

    async def delete(self, user: SelfBot) -> None:
        """
        Method to delete role.

        Parameters
        ----------
        user:
            Selfbot to send request.

        Raises
        ------
        HTTPTimeoutError
            Request reached http timeout limit.
        HTTPException
            Deleting the role failed.
        NotFound
            Role not found.
        Forbidden
            Selfbot doesn't have proper permissions.
        """
        await user.http.delete_role(user, guild_id=self.guild.id, role_id=self.id)

    async def edit(
        self,
        user: SelfBot,
        name: str | None = None,
        permissions: Permissions | None = None,
        color: Color | None = None,
        hoist: bool = False,
        mentionable: bool = False,
    ) -> Role:
        """
        Method to edit role.

        Parameters
        ----------
        user:
            Selfbot to send request.
        name:
            New role name.
        permissions:
            New role permissions.
        color:
            New role color.
        hoist:
            Whether this role should be hoist.
        mentionable:
            Whether this role should be mentionable.

        Raises
        ------
        HTTPTimeoutError
            Request reached http timeout limit.
        HTTPException
            Deleting the role failed.
        NotFound
            Role not found.
        Forbidden
            Selfbot doesn't have proper permissions.
        """
        params: dict[str, Any] = {
            "name": name,
            "permissions": permissions,
            "color": color.value if color else None,
            "hoist": hoist,
            "mentionable": mentionable,
        }

        for key, value in params.copy().items():
            if value is None:
                """
                If a parameter has a value of None,
                we don't want it in the dict because it could overwrite an already set parameter.
                """
                del params[key]

        data: dict[str, Any] = await user.http.edit_role(
            user, guild_id=self.guild.id, role=self, params=params
        )
        return Role(guild=self.guild, data=data)
