from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from os import PathLike


class File:
    """
    Represents a file.

    ..versionadded:: 1.2.0

    Parameters
    ----------
    fp: :class:`PathLike` | :class:`str` | :class:`bytes` | :class:`bytearray`
        The file path or bytes.
    name: :class:`str`
        The file name.
    spoiler: :class:`bool`
        Whether the file is a spoiler.
    description: Optional[:class:`str`]
        The file description.

    Attributes
    ----------
    fp: :class:`PathLike` | :class:`str` | :class:`bytes` | :class:`bytearray`
        The file path or bytes.
    name: :class:`str`
        The file name.
    spoiler: :class:`bool`
        Whether the file is a spoiler.
    description: Optional[:class:`str`]
        The file description.
    size: :class:`int`
        The file size.
    bytes: :class:`bytes`
        The file bytes.
    """

    def __init__(
        self,
        fp: PathLike | str | bytes | bytearray,
        name: str,
        spoiler: bool = False,
        description: str | None = None,
    ):
        self.fp: PathLike | str | bytes = fp
        self.name: str = name
        self.spoiler: bool = spoiler
        self.description: str | None = description

        if isinstance(self.fp, (bytes, bytearray)):
            self.bytes: bytes = self.fp
        else:
            with open(self.fp, mode="rb") as file:
                self.bytes: bytes = file.read()

        self.size: int = len(self.bytes)

    def __repr__(self) -> str:
        return f"<File(name={self.name}, spoiler={self.spoiler})>"

    def __eq__(self, other: File) -> bool:
        return (
            isinstance(other, File)
            and other.name == self.name
            and other.size == self.size
        )

    def __ne__(self, other: File) -> bool:
        return not self.__eq__(other)

    def __hash__(self) -> int:
        return hash((self.name, self.size, self.spoiler, self.description))
