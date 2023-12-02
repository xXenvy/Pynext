from __future__ import annotations
from typing import TYPE_CHECKING, Any

from .discorduser import DiscordUser

if TYPE_CHECKING:
    from .guild import Guild


class Application(DiscordUser):
    def __init__(self, guild: Guild, data: dict[str, Any]):
        super().__init__(guild._state, user_data=data["bot"])

        self.guild: Guild = guild

    def __repr__(self) -> str:
        return f"<Application(name={self.username}, id={self.id})>"
