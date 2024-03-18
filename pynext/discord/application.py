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

from .discorduser import DiscordUser

if TYPE_CHECKING:
    from ..state import State

    from .slash_command import SlashCommand


class Application(DiscordUser):
    """
    Represents the Application object.

    .. versionadded:: 1.0.8

    Parameters
    ----------
    state:
        State object.
    data:
        Application data.

    Attributes
    ----------
    raw_data: :class:`dict`
        Application raw data.
    name: :class:`str`
        Application name.
    description: :class:`str`
        Application description.
    global_name: Optional[:class:`str`]
        Application global name.
    username: :class:`str`
        Application username.
    discriminator: :class:`str`
        Application discriminator.
    avatar_id: Optional[:class:`str`]
        ID of the user avatar.
    id: :class:`int`
        Application unique ID.
    bot: :class:`bool`
        Whether user is classified as a bot.
    """

    __slots__ = (
        "raw_data",
        "guild",
        "name",
        "description",
        "application_id",
        "_commands",
    )

    def __init__(self, state: State, data: dict[str, Any]):
        super().__init__(state, user_data=data["bot"])

        self.raw_data: dict[str, Any] = data

        self.name: str = data["name"]
        self.description: str = data["description"]
        self._commands: dict[int, SlashCommand] = {}

        for app_command in data["app_commands"]:
            self._add_command(
                self._state.create_slash_command(application=self, data=app_command)
            )

    def __repr__(self) -> str:
        return f"<Application(name={self.username}, id={self.id})>"

    @property
    def commands(self) -> list[SlashCommand]:
        """
        Application slash commands.
        """
        return list(self._commands.values())

    def get_command_by_id(self, command_id: int) -> SlashCommand | None:
        """
        Method to get slash command by id.

        Parameters
        ----------
        command_id:
            Command id.
        """
        return self._commands.get(command_id)

    def get_command_by_name(self, command_name: str) -> SlashCommand | None:
        """
        Method to get slash command by name.

        Parameters
        ----------
        command_name:
            Command name.
        """
        for command in self.commands:
            if command.name == command_name:
                return command

    def _add_command(self, slash_command: SlashCommand) -> None:
        self._commands[slash_command.id] = slash_command

    def _remove_command(self, command_id: int) -> None:
        try:
            del self._commands[command_id]
        except KeyError:
            pass
