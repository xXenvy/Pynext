from __future__ import annotations
from typing import TYPE_CHECKING, Any

from ..utils import Hashable, snowflake_time, create_session
from ..enums import CommandOptionType
from ..errors import UnSupportedOptionType

from .role import Role

if TYPE_CHECKING:
    from datetime import datetime

    from ..state import State
    from ..selfbot import SelfBot

    from .application import Application
    from .guild import Guild
    from .channel import TextChannel


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

    __slots__ = (
        "_state",
        "application",
        "name",
        "description",
        "id",
        "type",
        "version_id",
        "_option_types"
    )

    def __init__(self, application: Application, data: dict[str, Any]):
        self._state: State = application._state
        self.application: Application = application

        self.name: str = data["name"]
        self.description: str = data["description"]
        self.id: int = int(data["id"])

        self.type: int = int(data["type"])
        self.version_id: int = int(data["version"])

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

    async def use(self, user: SelfBot, channel: TextChannel, **params) -> None:
        command_params: list[dict[str, Any]] = []

        for key, value in params.items():
            value_type, value = self._get_option_type(value)

            command_params.append(
                {
                    'name': key,
                    'value': value,
                    'type': value_type.value
                }
            )

        payload: dict[str, Any] = {
            'type': 2,
            'application_id': str(self.application.id),
            'guild_id': str(self.guild.id),
            'channel_id': str(channel.id),
            "session_id": create_session(),
            'data': {
                **self.to_dict(),
                "options": command_params
            }
        }
        print(payload)
        await self._state.http.use_interaction(
            user=user, payload=payload
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": str(self.id),
            "version": str(self.version_id),
            "name": self.name,
            "type": self.type,
        }

    def _get_option_type(self, value: Any) -> tuple[CommandOptionType, Any]:
        if isinstance(value, str):
            return CommandOptionType.STRING, value
        if isinstance(value, int):
            return CommandOptionType.INTEGER, value
        if isinstance(value, Role):
            return CommandOptionType.ROLE, value.id
        raise UnSupportedOptionType(f'Command does not support {type(value)} value type.')
