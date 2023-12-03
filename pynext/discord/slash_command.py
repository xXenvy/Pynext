from __future__ import annotations
from typing import TYPE_CHECKING, Any

from ..utils import Hashable, snowflake_time

if TYPE_CHECKING:
    from datetime import datetime

    from ..state import State

    from .application import Application
    from .guild import Guild


class SlashCommand(Hashable):
    """
    Represents the SlashCommand object.

    Parameters
    ----------
    application:
        Guild on which the application is.
    data:
        Slash command data.

    Attributes
    ----------
    application: :class:`Application`
        Slash command Application.
    name: :class:`str`
        Slash command name.
    description: :class:`str`
        Slash command description.
    id: :class:`int`
        Id of the command.
    type: :class:`int`
        Command Type.
    version_id:
        Autoincrementing version identifier updated during substantial record changes.
    """

    __slots__ = ("_state", "application", "name", "description", "id", "type", "version_id")

    def __init__(self, application: Application, data: dict[str, Any]):
        self._state: State = application._state
        self.application: Application = application

        self.name: str = data['name']
        self.description: str = data['description']
        self.id: int = int(data['id'])

        self.type: int = int(data['type'])
        self.version_id: int = int(data['version'])

    def __repr__(self) -> str:
        return f"<SlashCommand(name={self.name}, id={self.id})>"

    @property
    def guild(self) -> Guild:
        """
        Guild on which the slash command is.
        """
        return self.application.guild

    @property
    def version(self) -> datetime:
        """
        Datetime object of autoincrementing version updated during substantial record changes.
        """
        return snowflake_time(self.version_id)

    @property
    def created_at(self) -> datetime:
        """
        Datetime object of when the command was created.
        """
        return snowflake_time(self.id)
