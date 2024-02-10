from __future__ import annotations
from typing import Any, TypeVar, Generic, TYPE_CHECKING

from ..utils import create_session, nonce
from ..types import SelectMenuOption

from .emoji import Emoji
from .message import GuildMessage, PrivateMessage

if TYPE_CHECKING:
    from ..selfbot import SelfBot

MessageT = TypeVar("MessageT", GuildMessage, PrivateMessage)


class Button(Generic[MessageT]):
    """
    A class representing a Discord Button.

    .. versionadded:: 1.3.0

    Parameters
    ----------
    message: :class:`MessageT`
        The message that the button is in.
    row: :class:`int`
        The row number of the button.
    data: :class:`dict`
        The raw button data.

    Attributes
    ----------
    message: :class:`MessageT`
        The message that the button is in.
    row: :class:`int`
        The row number of the button.
    type: :class:`int`
        The button type.
    style: :class:`int`
        The button style.
    disabled: :class:`bool`
        Whether the button is disabled.
    url: Optional[:class:`str`]
        The button url.
    label: Optional[:class:`str`]
        The button label.
    custom_id: Optional[:class:`str`]
        The button custom id.
    emoji: Optional[:class:`Emoji`]
        The button emoji.
    """

    def __init__(self, message: MessageT, row: int, data: dict[str, Any]):
        self.message: MessageT = message
        self.row: int = row
        self.type: int = data["type"]

        self.style: int = data["style"]
        self.disabled: bool = data.get("disabled", False)

        self.url: str | None = data.get("url")
        self.label: str | None = data.get("label")

        self.custom_id: str | None = data.get("custom_id")
        self.emoji: Emoji | None = None

        if emoji_data := data.get("emoji"):
            self.emoji = Emoji(
                name=emoji_data["name"],
                animated=emoji_data.get("animated", False),
                emoji_id=emoji_data.get("id"),
            )

    def __repr__(self) -> str:
        return f"<Button(style={self.style}, label={self.label})>"

    def __hash__(self) -> int:
        return hash(
            (
                self.type,
                self.row,
                self.style,
                self.label,
                self.custom_id,
                self.emoji,
                self.message,
            )
        )

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Button) and hash(other) == hash(self)

    def __ne__(self, other: Any) -> bool:
        return not self.__eq__(other)

    async def use(self, selfbot: SelfBot) -> None:
        """
        Method to use the button.

        Parameters
        ----------
        selfbot: :class:`SelfBot`
            Selfbot to send the button interaction.

        Raises
        ------
        HTTPTimeoutError
            Request reached http timeout limit.
        HTTPException
            Using the button failed.
        NotFound
            Button not found.
        Forbidden
            Selfbot doesn't have proper permissions.
        ValueError
            If the button is a link button.
            Discord doesn't allow link buttons to be used.
        """
        if self.style == 5:
            raise ValueError("Cannot use a link button.")

        interaction_payload: dict[str, Any] = {
            "type": 3,
            "application_id": self.message.author_id,
            "channel_id": self.message.channel_id,
            "message_flags": self.message.flags,
            "message_id": self.message.id,
            "nonce": nonce(),
            "session_id": create_session(),
            "data": {
                "component_type": self.type,
                "custom_id": self.custom_id,
            },
        }
        if guild := getattr(self.message, "guild", None):
            interaction_payload["guild_id"] = guild.id

        await selfbot.http.use_interaction(selfbot, interaction_payload)


class SelectMenu(Generic[MessageT]):
    """
    A class representing a Discord SelectMenu.

    .. versionadded:: 1.3.0

    Parameters
    ----------
    message: :class:`MessageT`
        The message that the select menu is in.
    row: :class:`int`
        The row number of the select menu.
    data: :class:`dict`
        The raw select menu data.

    Attributes
    ----------
    message: :class:`MessageT`
        The message that the select menu is in.
    row: :class:`int`
        The row number of the select menu.
    type: :class:`int`
        The select menu type.
    custom_id: :class:`str`
        The select menu custom id.
    placeholder: Optional[:class:`str`]
        The select menu placeholder.
    disabled: :class:`bool`
        Whether the select menu is disabled.
    min_values: :class:`int`
        The select menu minimum values.
    max_values: :class:`int`
        The select menu maximum values.
    """

    def __init__(self, message: MessageT, row: int, data: dict[str, Any]):
        self.message: MessageT = message
        self.row: int = row

        self.options: list[SelectMenuOption] = []
        self.type: int = data["type"]
        self.custom_id: str = data["custom_id"]

        self.placeholder: str | None = data.get("placeholder")
        self.disabled: bool = data.get("disabled", False)

        self.min_values: int = data.get("min_values", 1)
        self.max_values: int = data.get("max_values", 1)

        for option in data.get("options", []):
            emoji_data: dict[str, Any] | None = option.get("emoji")
            if emoji_data:
                emoji = Emoji(
                    name=emoji_data["name"],
                    animated=emoji_data.get("animated", False),
                    emoji_id=emoji_data.get("id"),
                )
            else:
                emoji = None

            self.options.append(
                SelectMenuOption(
                    label=option["label"],
                    value=option["value"],
                    description=option.get("description"),
                    emoji=emoji,
                    default=option.get("default", False),
                )
            )

    def __repr__(self) -> str:
        return f"<SelectMenu(type={self.type}, custom_id={self.custom_id}, options={len(self.options)})>"

    def __hash__(self) -> int:
        return hash(
            (
                self.type,
                self.row,
                self.placeholder,
                self.min_values,
                self.max_values,
                self.custom_id,
                self.message,
            )
        )

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, SelectMenu) and hash(other) == hash(self)

    def __ne__(self, other: Any) -> bool:
        return not self.__eq__(other)

    def get_option_by_value(self, value: str) -> SelectMenuOption | None:
        """
        Method to get an option from the select menu by value.

        Parameters
        ----------
        value: :class:`str`
            The value of the option.
        """
        for option in self.options:
            if option.value == value:
                return option

    def get_option_by_label(self, label: str) -> SelectMenuOption | None:
        """
        Method to get an option from the select menu by label.

        Parameters
        ----------
        label: :class:`str`
            The label of the option.
        """
        for option in self.options:
            if option.label == label:
                return option

    async def use(self, selfbot: SelfBot, *options: SelectMenuOption) -> None:
        """
        Method to use the select menu.

        Parameters
        ----------
        selfbot: :class:`SelfBot`
            Selfbot to send the select menu interaction.
        options: :class:`SelectMenuOption`
            The options to use.

        Raises
        ------
        ValueError
            If the option is not in the select menu.
        HTTPTimeoutError
            Request reached http timeout limit.
        HTTPException
            Using the select menu failed.
        NotFound
            SelectMenu not found.
        Forbidden
            Selfbot doesn't have proper permissions.
        """
        interaction_payload: dict[str, Any] = {
            "type": 3,
            "application_id": self.message.author_id,
            "channel_id": self.message.channel_id,
            "message_flags": self.message.flags,
            "message_id": self.message.id,
            "nonce": nonce(),
            "session_id": create_session(),
            "data": {
                "component_type": self.type,
                "custom_id": self.custom_id,
                "values": [option.value for option in options],
            },
        }
        if guild := getattr(self.message, "guild", None):
            interaction_payload["guild_id"] = guild.id

        await selfbot.http.use_interaction(selfbot, interaction_payload)
