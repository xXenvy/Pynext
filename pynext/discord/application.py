from __future__ import annotations
from typing import TYPE_CHECKING, Any

from .discorduser import DiscordUser

if TYPE_CHECKING:
    from .guild import Guild


class Application(DiscordUser):
    """
    Represents the Application object.

    Parameters
    ----------
    guild:
        Guild on which the application is.
    data:
        Whether the emoji is animated.

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

    __slots__ = ("raw_data", "guild", "name", "description")

    def __init__(self, guild: Guild, data: dict[str, Any]):
        super().__init__(guild._state, user_data=data["bot"])
        self.raw_data: dict[str, Any] = data
        self.guild: Guild = guild

        self.name: str = data['name']
        self.description: str = data['description']

    def __repr__(self) -> str:
        return f"<Application(name={self.username}, id={self.id})>"
