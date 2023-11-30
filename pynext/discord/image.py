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
from typing import TYPE_CHECKING, ClassVar

if TYPE_CHECKING:
    from os import PathLike

    from ..state import State


class Image:
    """
    Representation of image implementation.

    Parameters
    ----------
    state:
        State object.
    url:
        Image url.
    animated:
        Whether the image is a animated (gif).

    Attributes
    ----------
    url: :class:`str`
        Image url.
    animated: :class:`bool`
        Whether the image is a animated (gif).
    """

    __slots__ = ("_state", "animated", "url")
    BASE_URL: ClassVar[str] = "https://cdn.discordapp.com"

    def __init__(self, state: State, url: str, animated: bool = False) -> None:
        self._state: State = state

        self.animated: bool = animated
        self.url: str = url

    def __repr__(self) -> str:
        return f"Image(url={self.url})"

    async def get_bytes(self) -> bytes:
        """
        Method to fetch image bytes.
        """
        return await self._state.http.get_image_bytes(url=self.url)

    async def save(self, path: PathLike | str) -> None:
        """
        Method to save image.
        """
        file_bytes: bytes = await self.get_bytes()

        with open(path, mode="wb") as file:
            file.write(file_bytes)

    @classmethod
    def _from_user(cls, state: State, user_id: int, avatar_id: str) -> Image:
        """
        Image constructor based on DiscordUser.

        Parameters
        ----------
        state:
            State object.
        user_id:
            Id of the user.
        avatar_id:
            Avatar id of the user.
        """
        animated: bool = avatar_id.startswith("a_")
        file_type: str = "gif" if animated else "webp"

        return cls(
            state=state,
            url=f"{cls.BASE_URL}/avatars/{user_id}/{avatar_id}.{file_type}?size=80",
            animated=animated,
        )

    @classmethod
    def _from_default_index(cls, state: State, avatar_id: str) -> Image:
        """
        Image constructor based on default avatar_id.

        Parameters
        ----------
        state:
            State object.
        avatar_id:
            Avatar id.
        """
        return cls(
            state=state,
            url=f"{cls.BASE_URL}/embed/avatars/{avatar_id}.png",
        )

    @classmethod
    def _from_guild_avatar(
        cls, state: State, guild_id: int, user_id: int, avatar_id: str
    ) -> Image:
        """
        Image constructor based on GuildMember.

        Parameters
        ----------
        state:
            State object.
        guild_id:
            Id of the guild.
        user_id:
            SelfBot id.
        avatar_id:
            Avatar id.
        """
        animated: bool = avatar_id.startswith("a_")
        file_type: str = "gif" if animated else "png"

        return cls(
            state=state,
            url=f"{cls.BASE_URL}/guilds/{guild_id}/users/{user_id}/avatars/{avatar_id}.{file_type}?size=1024",
            animated=animated,
        )

    @classmethod
    def _from_guild_icon(cls, state: State, guild_id: int, icon_id: str) -> Image:
        """
        Image constructor based on Guild.

        Parameters
        ----------
        state:
            State object.
        guild_id:
            Id of the guild.
        icon_id:
            Icon id.
        """
        animated: bool = icon_id.startswith("a_")
        file_type: str = "gif" if animated else "png"

        return cls(
            state=state,
            url=f"{cls.BASE_URL}/icons/{guild_id}/{icon_id}.{file_type}?size=1024",
            animated=animated,
        )
