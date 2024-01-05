from __future__ import annotations

from typing import Any, Generic, TypeVar

from ..utils import Hashable
from .message import GuildMessage, PrivateMessage

MessageT = TypeVar('MessageT', GuildMessage, PrivateMessage)


class Attachment(Hashable, Generic[MessageT]):

    def __init__(self, data: dict[str, Any], message: MessageT):
        self.message: MessageT = message
        self.id: int = int(data['id'])

        self.filename: str = data['filename']
        self.size: int = data['size']

        self.url: str = data['url']
        self.proxy_url: str = data['proxy_url']

        self.description: str | None = data.get('description')
        self.content_type: str | None = data.get('content_type')
        self.height: int | None = data.get('height')

        self.width: int | None = data.get('width')
        self.ephemeral: bool = data.get('ephemeral', False)
        self.duration_secs: float | None = data.get('duration_secs')

        self.waveform: str | None = data.get('waveform')
        self.flags: int | None = data.get('flags')

    def __repr__(self) -> str:
        return f"<Attachment(id={self.id}, filename={self.filename})>"
