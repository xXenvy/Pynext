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
from typing import Any


class PynextError(Exception):
    """Base exception class for pynext."""

    def __init__(self, value: Any):
        super().__init__(value)


class HTTPTimeoutError(PynextError):
    """Called when the request reaches the limit set in http_timeout."""


class HTTPException(PynextError):
    """Called if the status is not OK, and no others exceptions have been called."""


class BadRequest(PynextError):
    """400 status code."""


class Unauthorized(PynextError):
    """401 status code."""


class Forbidden(PynextError):
    """403 status code."""


class NotFound(PynextError):
    """404 status code."""


class CaptchaRequired(PynextError):
    """Called when the request was detected as blocked by hcaptcha."""


class FunctionIsNotCoroutine(PynextError):
    """Called when we specify a synchronous function to the event."""


class WebsocketNotConnected(PynextError):
    """Called when user doesn't have connection to the gateway."""


class VoiceStateNotFound(PynextError):
    """Called when user has no voice state set for the guild."""
