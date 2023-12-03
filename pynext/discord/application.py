from __future__ import annotations
from typing import TYPE_CHECKING, Any

from .discorduser import DiscordUser

if TYPE_CHECKING:
    from .guild import Guild
    from .slash_command import SlashCommand


class Application(DiscordUser):
    """
    Represents the Application object.

    Parameters
    ----------
    guild:
        Guild on which the application is.
    data:
        Application data.

    Attributes
    ----------
    raw_data: :class:`dict`
        Application raw data.
    guild: :class:`Guild`
        Guild on which the application is.
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

    def __init__(self, data: dict[str, Any], guild: Guild):
        super().__init__(guild._state, user_data=data["bot"])

        self.raw_data: dict[str, Any] = data
        self.guild: Guild = guild

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

    def _add_command(self, slash_command: SlashCommand) -> None:
        self._commands[slash_command.id] = slash_command

    def _remove_command(self, command_id: int) -> None:
        try:
            del self._commands[command_id]
        except KeyError:
            pass
