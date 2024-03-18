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
from typing import Iterable, Any

from ..errors import PynextError
from ..enums import PermissionsFlags
from .abc import BaseFlags


class Permissions(BaseFlags):
    """
    Representation of Permissions object.
    For more details, see: https://discord.com/developers/docs/topics/permissions#permissions

    **Example usage:**

    .. code-block:: python

        permissions: Permissions = Permissions(send_messages=False, view_channel=True)
        print(permissions.value)

    Parameters
    ----------
    value:
        Default bitwise value.
    permissions:
        Permissions with statuses.

    Attributes
    ----------
    value: :class:`int`
        Bitwise value of provided permissions.
    permission_flags: :class:`dict[PermissionsFlags, bool]`
        Dict with the flag object and its status.
    """

    __slots__ = ("_flags", "permission_flags", "value")

    def __init__(self, value: int = 0, **permissions: bool) -> None:
        self.value: int = value
        self.permission_flags: dict[PermissionsFlags, bool] = {}

        for permission, status in permissions.items():
            flag: PermissionsFlags | None = getattr(
                PermissionsFlags, permission.upper(), None
            )

            if not flag:
                raise PynextError(f"Invalid permission: {permission}")

            self.permission_flags[flag] = status

            if status is True:
                # If permission is enabled then this adds a bitwise value.
                self.value = self.value | flag.value

        self._flags: dict[PermissionsFlags, bool] = self.get_flags_by_value()

    def __repr__(self) -> str:
        return f"<Permissions(key={self.get_bitwise_by_flags()})>"

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, self.__class__) and other.value == self.value

    def __ne__(self, other: Any) -> bool:
        return not self.__eq__(other)

    def __hash__(self) -> int:
        return hash((self.value, self._flags))

    def __iter__(self) -> Iterable[tuple[PermissionsFlags, bool]]:
        for flag, status in self._flags.items():
            yield flag, status

    @classmethod
    def all(cls) -> Permissions:
        """
        Classmethod to create a permissions object with all permissions enabled.
        """
        return Permissions(value=-1)

    @classmethod
    def none(cls) -> Permissions:
        """
        Classmethod to create permissions object.
        """
        return Permissions()

    def add_flag(self, flag: PermissionsFlags, status: bool) -> None:
        """
        Method to add permission flag.

        Parameters
        ----------
        flag:
            Flag to add.
        status:
            Flag status.
        """
        self._flags[flag] = status

        if status is True:
            self.value = self.value | flag.value

    def get_flags_by_value(self) -> dict[PermissionsFlags, bool]:
        """
        Method to check what flags have status by bitwise value.
        """
        flags: dict[PermissionsFlags, bool] = {}

        for flag in PermissionsFlags:
            if (self.value & flag.value) == flag.value:
                flags[flag] = True
            else:
                flags[flag] = False

        return flags

    def get_bitwise_by_flags(self) -> int:
        """
        Method to calculate the bitwise value of all flags.
        """
        _value: int = 0

        for flag, status in self._flags.items():
            if status is True:
                _value = _value | flag.value

        return _value

    def update(self, permissions: Permissions) -> Permissions:
        """
        Method to update flags by another Permissions object.

        Parameters
        ----------
        permissions:
            Another permissions object.
        """
        old_flags: set = set(self._flags.items())
        new_flags: set = set(permissions._flags.items())
        flags_to_update: dict[PermissionsFlags, bool] = dict(new_flags - old_flags)

        for key, value in flags_to_update.items():
            if key in permissions.permission_flags:
                self._flags[key] = value
            else:
                # if we have a permissions flag to update,
                # which we have not entered in the permissions argument,
                # we want to set its parameter it already has
                # so if key to change is False it means the flag had a key True
                self._flags[key] = value is False

        return self

    @property
    def flags(self):
        """
        Permissions flags.
        """
        return self.get_flags_by_value()


class PermissionOverwrite:
    """
    Representation of PermissionOverwrite object.
    For more details, see: https://discord.com/developers/docs/topics/permissions#permission-overwrites

    **Example usage:**

    .. code-block:: python

        overwrite: PermissionOverwrite = PermissionOverwrite(send_messages=False, view_channel=True)
        print(overwrite.allow)
        print(overwrite.deny)

    Parameters
    ----------
    permissions:
        Permissions with statuses. Use None to set permission to default value.
    """

    __slots__ = ("_allow", "_deny")

    def __init__(self, **permissions: bool | None):
        self._allow: dict[PermissionsFlags, bool] = {}
        self._deny: dict[PermissionsFlags, bool] = {}

        for permission, status in permissions.items():
            flag: PermissionsFlags | None = getattr(
                PermissionsFlags, permission.upper(), None
            )

            if not flag:
                raise PynextError(f"Invalid permission type: {permission}")

            if status is False:
                self._deny[flag] = True
            elif status is True:
                self._allow[flag] = True

    def __repr__(self) -> str:
        allow: int = self.get_bitwise_by_flags(self._allow)
        deny: int = self.get_bitwise_by_flags(self._deny)

        return f"<PermissionOverwrite(allow={allow} deny={deny})>"

    @property
    def allow(self) -> Permissions:
        """
        Permission object only with allowed flags.
        """
        allow: Permissions = Permissions()

        for perm, status in self._allow.items():
            allow.add_flag(perm, status)

        return allow

    @property
    def deny(self) -> Permissions:
        """
        Permission object only with not allowed flags.
        """
        deny: Permissions = Permissions()

        for perm, status in self._deny.items():
            deny.add_flag(perm, status)

        return deny

    def pair(self) -> tuple[Permissions, Permissions]:
        """
        Tuple with allowed flags and disallowed flags.
        """
        return self.allow, self.deny

    @staticmethod
    def get_bitwise_by_flags(flags: dict[PermissionsFlags, bool]) -> int:
        """
        Method to calculate the bitwise value by provided flags.

        Parameters
        ----------
        flags:
            Flags to get bitwise value.
        """
        value: int = 0

        for flag, status in flags.items():
            if status is True:
                value = value | flag.value

        return value

    @classmethod
    def make_from_value(cls, allow: int = 0, deny: int = 0) -> PermissionOverwrite:
        """
        Classmethod to create overwrite via bitwise values.

        Parameters
        ----------
        allow:
            Bitwise value of allowed permissions.
        deny:
            Bitwise value of not allowed permissions.
        """
        allow_permissions: Permissions = Permissions(value=allow)
        deny_permissions: Permissions = Permissions(value=deny)

        allow_flags = set(allow_permissions.flags.items())
        deny_flags = set(deny_permissions.flags.items())
        flags: dict = dict(allow_flags - deny_flags)

        return cls(**{flag.name: status for flag, status in flags.items()})

    @classmethod
    def make_from_permissions(
        cls,
        allow: Permissions = Permissions.none(),
        deny: Permissions = Permissions.none(),
    ) -> PermissionOverwrite:
        """
        Classmethod to create overwrite via permissions objects.

        Parameters
        ----------
        allow:
            Permissions object of allowed permissions.
        deny:
            Permissions object of not allowed permissions.
        """
        return cls.make_from_value(allow=allow.value, deny=deny.value)
