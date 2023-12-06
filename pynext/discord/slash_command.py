from __future__ import annotations
from typing import TYPE_CHECKING, Any

from ..utils import Hashable, snowflake_time, create_session
from ..enums import CommandOptionType
from ..errors import UnSupportedOptionType
from ..types import ApplicationCommandOption

from .role import Role
from .permissions import Permissions
from .discorduser import DiscordUser
from .channel import TextChannel, DMChannel, BaseChannel

if TYPE_CHECKING:
    from datetime import datetime

    from ..state import State
    from ..selfbot import SelfBot

    from .application import Application


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
        Command name.
    description: :class:`str`
        Command description.
    id: :class:`int`
        Id of the command.
    type: :class:`int`
        Command Type.
    version_id: :class:`int`
        Autoincrementing version identifier updated during substantial record changes.
    """

    __slots__ = ("name", "description", "id", "type", "version_id", "_sub_commands")

    def __init__(self, data: dict[str, Any]):
        self.name: str = data["name"]
        self.description: str = data["description"]
        self.id: int = int(data["id"])
        self.type: int = int(data["type"])
        self.version_id: int = int(data["version"])

        self._sub_commands: dict[str, SubCommand] = {}

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

    def get_sub_command(self, name: str) -> SubCommand | None:
        """
        Method to get subcommand by name.

        Parameters
        ----------
        name:
            Subcommand name.
        """
        return self._sub_commands.get(name)

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

    def _add_sub_command(self, subcommand: SubCommand) -> None:
        self._sub_commands[subcommand.name] = subcommand

    def _remove_sub_command(self, name: str) -> None:
        try:
            del self._sub_commands[name]
        except KeyError:
            pass

    @staticmethod
    def _get_option_type(value: Any) -> tuple[CommandOptionType, Any]:
        if isinstance(value, str):
            return CommandOptionType.STRING, value
        if isinstance(value, int):
            return CommandOptionType.INTEGER, value
        if isinstance(value, float):
            return CommandOptionType.NUMBER, value
        if isinstance(value, bool):
            return CommandOptionType.BOOLEAN, value
        if isinstance(value, Role):
            return CommandOptionType.ROLE, value.id
        if isinstance(value, DiscordUser):
            return CommandOptionType.USER, value.id
        if isinstance(value, BaseChannel):
            return CommandOptionType.CHANNEL, value.id

        raise UnSupportedOptionType(
            f"Command does not support {type(value)} value type."
        )


class SlashCommand(BaseCommand):
    """
    Represents the SlashCommand object.

    .. versionadded:: 1.0.8

    Parameters
    ----------
    application:
        Application to which the command is assigned.
    data:
        Slash command data.

    Attributes
    ----------
    application: :class:`Application`
        SlashCommand application object.
    options: list[:class:`ApplicationCommandOption`]
        SubCommand options.
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
        "application",
        "options",
        "default_member_permissions",
    )

    def __init__(self, application: Application, data: dict[str, Any]):
        super().__init__(data)
        self._state: State = application._state

        self.application: Application = application
        self.options: list[ApplicationCommandOption] = []
        self.default_member_permissions: Permissions | None = None

        if permissions := data.get("default_member_permissions"):
            self.default_member_permissions = Permissions(int(permissions))

        for option_data in data.get("options", []):
            if option_data["type"] in (1, 2):
                self._add_sub_command(
                    self._state.create_sub_command(parent=self, data=option_data)
                )
            else:
                self.options.append(
                    ApplicationCommandOption(
                        type=option_data["type"],
                        name=option_data["name"],
                        description=option_data["description"],
                        required=option_data.get("required", False),
                        autocomplete=option_data.get("autocomplete", False),
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

    async def use(
        self, user: SelfBot, channel: TextChannel | DMChannel, **params
    ) -> None:
        """
        Method to use application command.

        Parameters
        ----------
        user:
            Selfbot to use the command.
        channel:
            Channel on which the command is supposed to be used.
        params:
            Command arguments.

        Raises
        ------
        HTTPTimeoutError
            Request reached http timeout limit.
        HTTPException
            Using the command failed.
        NotFound
            Command not found.
        Forbidden
            Selfbot doesn't have proper permissions.
        UnSupportedOptionType
            Command does not support the specified option type.
        """
        command_params: list[dict[str, Any]] = []

        for key, value in params.items():
            value_type, value = self._get_option_type(value)

            command_params.append(
                {"name": key, "value": value, "type": value_type.value}
            )

        payload: dict[str, Any] = {
            "type": 2,
            "application_id": str(self.application.id),
            "channel_id": str(channel.id),
            "session_id": create_session(),
            "data": {**self.to_dict(), "options": command_params},
        }

        if isinstance(channel, TextChannel):
            payload["guild_id"] = channel.guild.id

        await self._state.http.use_interaction(user=user, payload=payload)


class SubCommand(BaseCommand):
    """
    Represents the SubCommand object.

    .. versionadded:: 1.0.8

    Parameters
    ----------
    parent:
        SlashCommand / SubCommand to which the command is assigned.
    data:
        Slash command data.

    Attributes
    ----------
    parent: Union[:class:`SlashCommand`, :class:`SubCommand`]
        SubCommand parent.
    application: :class:`Application`
        SlashCommand application object.
    options: list[:class:`ApplicationCommandOption`]
        SubCommand options.
    name: :class:`str`
        SubCommand name.
    description: :class:`str`
        SubCommand description.
    id: :class:`int`
        Id of the command.
    type: :class:`int`
        Command Type.
    version_id: :class:`int`
        Autoincrementing version identifier updated during substantial record changes.
    """

    __slots__ = ("_state", "application", "options", "parent")

    def __init__(self, parent: SlashCommand | SubCommand, data: dict[str, Any]):
        super().__init__(data)

        self._state: State = parent._state

        self.parent: SlashCommand | SubCommand = parent
        self.application: Application = parent.application
        self.options: list[ApplicationCommandOption] = []

        for option_data in data.get("options", []):
            if option_data["type"] == 1:
                self._add_sub_command(
                    self._state.create_sub_command(parent=self, data=option_data)
                )
            else:
                self.options.append(
                    ApplicationCommandOption(
                        type=option_data["type"],
                        name=option_data["name"],
                        description=option_data["description"],
                        required=option_data.get("required", False),
                        autocomplete=option_data.get("autocomplete", False),
                    )
                )

    def __repr__(self) -> str:
        return f"<SubCommand(name={self.name}, id={self.id})>"

    async def use(
        self, user: SelfBot, channel: TextChannel | DMChannel, **params
    ) -> None:
        """
        Method to use application command.

        Parameters
        ----------
        user:
            Selfbot to use the command.
        channel:
            Channel on which the command is supposed to be used.
        params:
            Command arguments.

        Raises
        ------
        HTTPTimeoutError
            Request reached http timeout limit.
        HTTPException
            Using the command failed.
        NotFound
            Command not found.
        Forbidden
            Selfbot doesn't have proper permissions.
        UnSupportedOptionType
            Command does not support the specified option type.
        """
        payload: dict[str, Any] = {
            "type": 2,
            "application_id": str(self.application.id),
            "channel_id": str(channel.id),
            "session_id": create_session(),
            "data": self.__format_options_payload(params),
        }
        if isinstance(channel, TextChannel):
            payload["guild_id"] = channel.guild.id

        await self._state.http.use_interaction(user=user, payload=payload)

    def __format_options_payload(self, params: dict[str, Any]) -> dict[str, Any]:
        # Don't ask what's going on here. It just works.

        slash_command: SubCommand | SlashCommand = self
        sub_commands: list[SubCommand | SlashCommand] = [slash_command]

        while True:
            sub_commands.append(slash_command.parent)
            slash_command = slash_command.parent

            if isinstance(slash_command, SlashCommand):
                break

        options: dict[str, Any] = {}

        for index, cmd in enumerate(reversed(sub_commands)):
            if index == 0:
                options = {
                    "type": 1,
                    "name": cmd.name,
                    "id": cmd.id,
                    "version": cmd.version_id,
                    "options": [{}],
                }
            else:
                data: dict[str, Any] = options
                for _ in range(index):
                    data = data["options"][0]

                data["type"] = cmd.type
                data["name"] = cmd.name
                data["options"] = [{}]

                if index == len(sub_commands) - 1:
                    command_params: list[dict[str, Any]] = []

                    for key, value in params.items():
                        value_type, value = self._get_option_type(value)

                        command_params.append(
                            {"name": key, "value": value, "type": value_type.value}
                        )

                    data["options"] = command_params

        return options
