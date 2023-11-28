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
from typing import Literal, TYPE_CHECKING, Any

if TYPE_CHECKING:
    from discord_typings import Snowflake


class Route:
    """
    Representation of Route structure.
    Route includes fundamental information about the request we want to send.

    Parameters
    ----------
    method:
        HTTP request method.
    url:
        HTTP request url.
    headers:
        HTTP request headers.
    params:
        Parameters to format the url.

    Attributes
    ----------
    method:
        HTTP request method.
    url:
        HTTP request url.
    headers:
        HTTP request headers.
    """
    __slots__ = ("method", "url", "headers")

    def __init__(
            self,
            method: Literal[
                "GET",
                "POST",
                "PUT",
                "DELETE",
                "PATCH"],
            url: str,
            headers: dict[str, Any] | None = None,
            **params: Snowflake):

        self.method: str = method
        self.url: str = url.format(**params)
        self.headers: dict[str, Any] = {} if headers is None else headers

    def __repr__(self) -> str:
        return f"<Route(method={self.method}, url={self.url})>"
