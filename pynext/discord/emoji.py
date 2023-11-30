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


class Emoji:
    """
    Represents the Emoji object.

    Parameters
    ----------
    name:
        Emoji name.
    animated:
        Whether the emoji is animated.
    emoji_id:
        Emoji ID. If it has.

    Attributes
    ----------
    name: :class:`str`
        Emoji name.
    animated: :class:`bool`
        Whether the emoji is animated.
    id: Optional[:class:`int`]
        Emoji ID. If it has.
    encode: :class:`str`
        Emoji encode format.
    """

    __slots__ = ("name", "animated", "id", "encode")

    def __init__(self, name: str, animated: bool = False, emoji_id: int | None = None):
        self.name: str = name

        self.animated: bool = animated
        self.id: int | None = emoji_id

        if not self.id:
            self.encode: str = self.name
        else:
            self.encode: str = (
                f"{self.name}:{self.id}" if not animated else f"a:{self.name}:{self.id}"
            )

    def __repr__(self) -> str:
        return f"<Emoji(name={self.name}, id={self.id})>"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, self.__class__) and other.unique_id == self.unique_id

    def __ne__(self, other: object) -> bool:
        if isinstance(other, self.__class__):
            return other.unique_id != self.unique_id
        return True

    def __hash__(self) -> int:
        return hash((self.name, self.animated, self.id))

    @property
    def unique_id(self) -> int:
        """
        Unique emoji object id.
        """
        return self.__hash__()

    def to_dict(self) -> dict:
        """
        Method converts data to dict.
        """
        return {"id": self.id, "name": self.name, "animated": self.animated}
