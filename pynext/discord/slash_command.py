from __future__ import annotations
from typing import TYPE_CHECKING, Any

from ..utils import Hashable, snowflake_time, create_session
from ..enums import CommandOptionType
from ..errors import UnSupportedOptionType
from ..types import ApplicationCommandOption

from .role import Role
from .permissions import Permissions

if TYPE_CHECKING:
    from datetime import datetime

    from ..state import State
    from ..selfbot import SelfBot

    from .application import Application
    from .guild import Guild
    from .channel import TextChannel


class BaseCommand(Hashable):
    """
    Represents the BaseCommand object.

    Parameters
    ----------
    data:
        Command data.

    Attributes
    ----------
    name: :class:`str`
        Slash command name.
    description: :class:`str`
        Slash command description.
    id: :class:`int`
        Id of the command.
    type: :class:`int`
        Command Type.
    """
    __slots__ = (
        "name",
        "description",
        "id",
        "type",
        "_sub_commands"
    )

    def __init__(self, data: dict[str, Any]):
        self.name: str = data["name"]
        self.description: str = data["description"]
        self.id: int = int(data["id"])
        self.type: int = int(data["type"])

        self._sub_commands: dict[int, SubCommand] = {}

    @property
    def created_at(self) -> datetime:
        """
        Datetime object of when the command was created.
        """
        return snowflake_time(self.id)

    @property
    def sub_commands(self) -> list[SubCommand]:
        """
        Command subcommands
        """
        return list(self._sub_commands.values())

    def _add_sub_command(self, subcommand: SubCommand) -> None:
        self._sub_commands[subcommand.id] = subcommand

    def _remove_sub_command(self, subcommand_id: int) -> None:
        try:
            del self._sub_commands[subcommand_id]
        except KeyError:
            pass


class SlashCommand(BaseCommand):
    """
    Represents the SlashCommand object.

    Parameters
    ----------
    application:
        Application to which the command is assigned.
    data:
        Slash command data.

    Attributes
    ----------
    name: :class:`str`
        Slash command name.
    description: :class:`str`
        Slash command description.
    id: :class:`int`
        Id of the command.
    type: :class:`int`
        Command Type.
    version_id: :class:`int`
        Autoincrementing version identifier updated during substantial record changes.
    default_member_permissions: Optional[:class:`Permissions`]
        Command permissions.
    """

    __slots__ = (
        "_state",
        "_sub_commands",
        "application",
        "options",
        "version_id",
        "default_member_permissions"
    )

    def __init__(self, application: Application, data: dict[str, Any]):
        super().__init__(data)
        self._state: State = application._state

        self.application: Application = application
        self.options: list[ApplicationCommandOption] = []
        self.version_id: int = int(data["version"])
        self.default_member_permissions: Permissions | None = None

        if permissions := data.get('default_member_permissions'):
            self.default_member_permissions = Permissions(int(permissions))

        for option_data in data.get('options', []):
            if option_data['type'] == 1:
                self._add_sub_command(
                    self._state.create_sub_command(
                        parent=self,
                        data=option_data
                    )
                )
            else:
                self.options.append(
                    ApplicationCommandOption(
                        type=option_data['type'],
                        name=option_data['name'],
                        description=option_data['description'],
                        required=option_data.get('required', False),
                        autocomplete=option_data.get('autocomplete', False)
                    )
                )

    def __repr__(self) -> str:
        return f"<SlashCommand(name={self.name}, id={self.id})>"

    @property
    def version(self) -> datetime:
        """
        Datetime object of autoincrementing version updated during substantial record changes.
        """
        return snowflake_time(self.version_id)

    @property
    def guild(self) -> Guild:
        """
        Guild on which the slash command is.
        """
        return self.application.guild

    async def use(self, user: SelfBot, channel: TextChannel, **params) -> None:
        command_params: list[dict[str, Any]] = []

        for key, value in params.items():
            value_type, value = self._get_option_type(value)

            command_params.append(
                {"name": key, "value": value, "type": value_type.value}
            )

        payload: dict[str, Any] = {
            "type": 2,
            "application_id": str(self.application.id),
            "guild_id": str(self.guild.id),
            "channel_id": str(channel.id),
            "session_id": create_session(),
            "data": {**self.to_dict(), "options": command_params},
        }
        await self._state.http.use_interaction(user=user, payload=payload)

    def to_dict(self) -> dict[str, Any]:
        """
        Method to convert class attributes to dict.
        """
        return {
            "id": str(self.id),
            "version": str(self.version_id),
            "name": self.name,
            "type": self.type,
        }

    @staticmethod
    def _get_option_type(value: Any) -> tuple[CommandOptionType, Any]:
        if isinstance(value, str):
            return CommandOptionType.STRING, value
        if isinstance(value, int):
            return CommandOptionType.INTEGER, value
        if isinstance(value, Role):
            return CommandOptionType.ROLE, value.id
        raise UnSupportedOptionType(
            f"Command does not support {type(value)} value type."
        )


class SubCommand(BaseCommand):
    """
    Represents the SubCommand object.

    Parameters
    ----------
    parent:
        SlashCommand / SubCommand to which the command is assigned.
    data:
        Slash command data.

    Attributes
    ----------
    name: :class:`str`
        SubCommand name.
    description: :class:`str`
        SubCommand description.
    id: :class:`int`
        Id of the command.
    type: :class:`int`
        Command Type.
    default_member_permissions: Optional[:class:`Permissions`]
        Command permissions.
    """

    __slots__ = (
        "_state",
        "application",
        "options",
        "parent"
    )

    def __init__(self, parent: SlashCommand | SubCommand, data: dict[str, Any]):
        data['id'] = parent.id
        super().__init__(data)

        print(data)

        self._state: State = parent._state

        self.parent: SlashCommand | SubCommand = parent
        self.application: Application = parent.application
        self.options: list[ApplicationCommandOption] = []

    def __repr__(self) -> str:
        return f"<SubCommand(name={self.name}, id={self.id})>"

    @property
    def guild(self) -> Guild:
        """
        Guild on which the slash command is.
        """
        return self.application.guild
