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
from typing import Literal, Any, TYPE_CHECKING

from time import time

from ..enums import GatewayCodes, StatusType
from ..errors import PynextError

if TYPE_CHECKING:
    from .activity import Activity


class PresenceBuilder:
    """
    PresenceBuilder handles presence building for selfbots.

    Parameters
    ----------
    status:
        Selfbot status.
    afk:
        Whether or not the client is afk.
    since:
        Unix time (in milliseconds) of when the client went idle, or null if the client is not idle.
    activities:
        User's activities.

    Attributes
    ----------
    status: :class:`Union[Literal['online', 'dnd', 'idle', 'invisible', 'offline'] | StatusType]`
        Selfbot status.
    afk: :class:`bool`
        Whether or not the client is afk.
    since: Optional[:class:`int`]
        Unix time (in milliseconds) of when the client went idle, or null if the client is not idle.
    activities: :class:`list[Activity]`
        User's activities.

    Raises
    ------
    PynextError
        Invalid status type. Expected str or StatusType.
    """

    __slots__ = ("status", "since", "afk", "activities")

    def __init__(
        self,
        status: Literal["online", "dnd", "idle", "invisible", "offline"]
        | StatusType = "online",
        afk: bool = False,
        since: int | None = None,
        activities: list[Activity] | None = None,
    ):
        self.activities: list[Activity] = activities or []

        if isinstance(status, StatusType):
            status = status.value

        if not isinstance(status, str):
            raise PynextError(
                f"Invalid status type. Expected str or StatusType, received: {type(status)}"
            )

        self.status = status
        self.since: int = since or int(time())
        self.afk: bool = afk

    def __repr__(self) -> str:
        return f"<PresenceBuilder(status={self.status})>"

    def __hash__(self) -> int:
        return hash((self.status, self.afk, self.since, self.activities))

    def __eq__(self, other: object) -> bool:
        return isinstance(other, self.__class__) and other.unique_id == self.unique_id

    def __ne__(self, other: object) -> bool:
        if isinstance(other, self.__class__):
            return other.unique_id != self.unique_id
        return True

    @property
    def unique_id(self) -> int:
        """
        PresenceBuilder unique id.
        """
        return self.__hash__()

    def to_dict(self) -> dict[str, Any]:
        """
        Method to format all data into a dict.
        """
        return {
            "op": GatewayCodes.PRESENCE.value,
            "d": {
                "since": self.since,
                "activities": [activity.to_dict() for activity in self.activities],
                "status": self.status,
                "afk": self.afk,
            },
        }
