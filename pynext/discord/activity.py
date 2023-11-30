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

from time import time
import re

from ..enums import ActivityType
from ..errors import PynextError
from .reaction import Emoji


class Activity:
    """
    Representation of activity implementation.

    Parameters
    ----------
    name:
        Activity name.
    activity_type:
        Type of activity.
    application_id:
        Application ID for the game
    details:
        What the selfbot is currently doing.
    state:
        SelfBot's current party status, or text used for a custom status
    url:
        Url to stream from youtube or twitch. It only works if the activity type is on 1 (Streaming).
    emoji:
        Emoji used for a custom status.
    large_image:
        Url to large image.
    large_text:
        Text displayed when hovering over the large image of the activity.
    small_image:
        Url to small image.
    small_text:
        Text displayed when hovering over the small image of the activity.

    Attributes
    ----------
    name: :class:`str`
        Activity name.
    activity_type: Union[:class:`pynext.enums.ActivityType`, :class:`int`]
        Type of activity.
    application_id: Optional[:class:`int`]
        Application ID for the game
    details: Optional[:class:`str`]
        What the selfbot is currently doing.
    state: Optional[:class:`str`]
        SelfBot's current party status, or text used for a custom status
    url: Optional[:class:`str`]
        Url to stream from youtube or twitch. It only works if the activity type is on 1 (Streaming).
    emoji_data: Optional[:class:`str`]
        Emoji data used for a custom status.
    large_image: Optional[:class:`str`]
        Url to large image.
    large_text: Optional[:class:`str`]
        Text displayed when hovering over the large image of the activity.
    small_image: Optional[:class:`str`]
        Url to small image.
    small_text: Optional[:class:`str`]
        Text displayed when hovering over the small image of the activity.
    """

    __slots__ = (
        "name",
        "emoji_data",
        "created_at",
        "details",
        "state",
        "activity_type",
        "url",
        "large_image",
        "large_text",
        "small_image",
        "small_text",
        "application_id",
    )

    def __init__(
        self,
        name: str,
        activity_type: ActivityType | int,
        application_id: int | None = None,
        details: str | None = None,
        state: str | None = None,
        url: str | None = None,
        emoji: Emoji | None = None,
        large_image: str | None = None,
        large_text: str | None = None,
        small_image: str | None = None,
        small_text: str | None = None,
    ):
        self.name: str = name
        self.application_id: int | None = application_id
        self.emoji_data: dict | None = (
            emoji.to_dict() if isinstance(emoji, Emoji) else None
        )
        self.created_at: int = int(time())
        self.details: str | None = details
        self.state: str | None = state

        self.large_image: str | None = large_image
        self.large_text: str | None = large_text
        self.small_image: str | None = small_image
        self.small_text: str | None = small_text

        if isinstance(activity_type, ActivityType):
            self.activity_type: int = activity_type.value
        else:
            self.activity_type: int = activity_type

        if url is not None:
            self._validate_url(url)

        self.url: str | None = url

    def __repr__(self) -> str:
        return f"<Activity(name={self.name})>"

    def _validate_url(self, url: str):
        if self.activity_type != 1:
            # According to discord docs, links only work when ActivityType is set to 1 (Streaming)
            raise PynextError(
                "The url parameter can only be used if ActivityType is Streaming."
            )

        youtube_regex = r"(https?://)?(www\.)?youtube\.(com|nl)/watch\?v=([-\w]+)"
        match: re.Match | None = re.match(youtube_regex, url)

        # If the regex did not find the youtube link and there is no twitch in the url
        if not match and "twitch" not in url:
            raise PynextError("Discord supports youtube and twitch links only.")

    def to_dict(self) -> dict:
        """
        Method to convert all information to dict.
        """
        return {
            "name": self.name,
            "type": self.activity_type,
            "emoji": self.emoji_data,
            "since": 0,
            "application_id": str(self.application_id) if self.application_id else None,
            "created_at": self.created_at,
            "url": self.url,
            "details": self.details,
            "_state": self.state,
            "assets": {
                "large_text": self.large_text,
                "large_image": self.large_image,
                "small_text": self.small_text,
                "small_image": self.small_image,
            },
        }
