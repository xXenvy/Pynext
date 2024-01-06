from __future__ import annotations

from typing import Any, Generic, TypeVar

from ..utils import Hashable
from .message import GuildMessage, PrivateMessage

MessageT = TypeVar("MessageT", GuildMessage, PrivateMessage)


class Attachment(Hashable, Generic[MessageT]):
    """
    Represents an attachment in a message.

    .. versionadded:: 1.2.0

    Parameters
    ----------
    data: dict[str, Any]
        The data of the attachment.
    message: MessageT
        The message this attachment is attached to.

    Attributes
    ----------
    message: MessageT
        The message this attachment is attached to.
    id: int
        The attachment's ID.
    filename: str
        The attachment's filename.
    size: int
        The attachment's size.
    url: str
        The attachment's URL.
    proxy_url: str
        The attachment's proxy URL.
    description: Optional[str]
        The attachment's description.
    content_type: Optional[str]
        The attachment's content type.
    height: Optional[int]
        The attachment's height.
    width: Optional[int]
        The attachment's width.
    ephemeral: bool
        Whether the attachment is ephemeral.
    duration_secs: Optional[float]
        The attachment's duration in seconds.
    waveform: Optional[str]
        The attachment's waveform.
    flags: Optional[int]
        The attachment's flags.
    """
    def __init__(self, data: dict[str, Any], message: MessageT):
        self.message: MessageT = message
        self.id: int = int(data["id"])

        self.filename: str = data["filename"]
        self.size: int = data["size"]

        self.url: str = data["url"]
        self.proxy_url: str = data["proxy_url"]
        self.spoiler: bool = self.filename.startswith("SPOILER")

        self.description: str | None = data.get("description")
        self.content_type: str | None = data.get("content_type")
        self.height: int | None = data.get("height")

        self.width: int | None = data.get("width")
        self.ephemeral: bool = data.get("ephemeral", False)
        self.duration_secs: float | None = data.get("duration_secs")

        self.waveform: str | None = data.get("waveform")
        self.flags: int | None = data.get("flags")

    def __repr__(self) -> str:
        return f"<Attachment(id={self.id}, filename={self.filename})>"

    def to_dict(self) -> dict[str, Any]:
        """
        Converts the attachment to a dict.
        """
        return {
            "id": self.id,
            "filename": self.filename,
            "size": self.size,
            "url": self.url,
            "proxy_url": self.proxy_url,
            "description": self.description,
            "content_type": self.content_type,
            "height": self.height,
            "width": self.width,
            "ephemeral": self.ephemeral,
            "duration_secs": self.duration_secs,
            "waveform": self.waveform,
            "flags": self.flags,
        }
