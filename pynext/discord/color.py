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
from typing import Any

from ..errors import PynextError


class Color:
    """
    Represents the Color object.

    Parameters
    ----------
    value:
        Raw integer color value.

    Attributes
    ----------
    value: :class:`int`
        Raw integer color value.
    """

    __slots__ = ("value",)

    def __init__(self, value: int):
        if not isinstance(value, int):
            raise PynextError(
                f"Expected int parameter, received {type(value)} instead."
            )

        self.value: int = value

    def _get_byte(self, byte: int) -> int:
        return (self.value >> (8 * byte)) & 0xFF

    def _get_rgb(self) -> tuple[int, int, int]:
        return self._get_byte(2), self._get_byte(1), self._get_byte(0)

    def __hash__(self) -> int:
        return hash(self.value)

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, self.__class__) and other.value == self.value

    def __ne__(self, other: Any) -> bool:
        return not self.__eq__(other)

    def __int__(self) -> int:
        return self.value

    def __repr__(self) -> str:
        return f"<Color(value={self.value})>"

    def to_rgb(self) -> tuple[int, int, int]:
        """
        Method to convert color raw value to rgb.
        """
        return self._get_rgb()

    def to_hex(self) -> str:
        """
        Method to convert color raw value to hex.
        """
        return hex(self.value)

    @classmethod
    def from_hex(cls, hex_color: str) -> Color:
        """
        Classmethod to create a Color object via hex.

        Parameters
        ----------
        hex_color:
            Hex color.
        """
        try:
            value: int = int(hex_color.replace("#", ""), 16)
        except ValueError:
            raise PynextError("You specified an invalid hex key.")

        return cls(value)

    @classmethod
    def from_rgb(cls, r: int, g: int, b: int) -> Color:
        """
        Classmethod to create a Color object via rgb values.

        Parameters
        ----------
        r:
            Red value.
        g:
            Green value.
        b:
            Blue value.
        """
        return cls((r << 16) + (g << 8) + b)
