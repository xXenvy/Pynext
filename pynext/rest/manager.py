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
from typing import TYPE_CHECKING, Any, Callable, Optional

from asyncio import sleep
from logging import Logger, getLogger

from ..utils import text_or_json
from ..errors import NotFound, Forbidden, Unauthorized, CaptchaRequired, HTTPException, BadRequest

if TYPE_CHECKING:
    from aiohttp import ClientResponse

    from .route import Route
    from .httpclient import HTTPClient


class ContextHandler:
    """
    RequestManager helping HTTP client. It handles configured delays, ratelimit and error handling.

    Parameters
    ----------
    http:
        HTTP Client.
    additional_delay:
        Additional ratelimit delay, which is added when you reach ratelimit.

    Attributes
    ----------
    http:
        HTTP Client.
    additional_delay:
        Additional ratelimit delay, which is added when you reach ratelimit.
    ratelimited:
        Whether the ContextHandler is ratelimited.
    logger:
        Logger to log ratelimits.
    errors:
        Dict with errors to call when the request receives the specified status code.
    """
    __slots__ = ("additional_delay", "http", "ratelimited", "logger", "errors")

    def __init__(self, http: HTTPClient, additional_delay: float):
        self.http: HTTPClient = http
        self.additional_delay: float = additional_delay
        self.ratelimited: bool = False

        self.logger: Logger = getLogger("pynext.rest")
        self.errors: dict[int, Callable] = {
            400: BadRequest, 404: NotFound,
            401: Unauthorized, 403: Forbidden
        }

    def __repr__(self) -> str:
        return f"<RequestHandler(ratelimited={self.ratelimited}, delay={self.additional_delay})>"

    def is_ratelimited(self, response: ClientResponse) -> bool:
        """
        Method to check by request whether we have reached ratelimit.

        Parameters
        ----------
        response:
            Response to check status.
        """
        if response.status == 429:
            self.ratelimited = True

        return response.status == 429

    @staticmethod
    async def is_blocked_by_captcha(response: ClientResponse) -> bool:
        """
        Method to check if request has been blocked by captcha.

        Parameters
        ----------
        response:
            Request response to check.
        """
        if response.status != 400:
            return False

        data: dict[str, Any] | str = await text_or_json(response)
        if isinstance(data, str):
            return "hcaptcha" in data

        return bool(data.get('captcha_key', False))

    async def handle_errors(self, response: ClientResponse) -> None:
        """
        Method to handle error calls.

        Parameters
        ----------
        response:
            Request response to check.

        Raises
        ------
        CaptchaRequired
            Request has been blocked by captcha.
        HTTPException
            There was an HTTP error.
        BadRequest
            Request raises BadRequest error.
        NotFound
            Request raises NotFound error.
        Unauthorized
            Request raises Unauthorized error.
        Forbidden
            Request raises Forbidden error.
        """
        if await self.is_blocked_by_captcha(response):
            raise CaptchaRequired("Request has been blocked by hcaptcha.")

        error: Optional[Callable] = self.errors.get(response.status)
        if error is not None:
            raise error(await text_or_json(response))

        if response.status not in (200, 204, 201):
            raise HTTPException(await text_or_json(response))

    async def handle_ratelimit(
            self,
            retry_after: float,
            route: Route,
            json: dict | None = None
    ) -> ClientResponse:
        """
        Method to handle ratelimit.

        Parameters
        ----------
        retry_after:
            Time in seconds to release a request.
        route:
            Route required to build the re-request.
        json:
            Json data to build the re-request.
        """
        retry_after += self.additional_delay

        request: dict[str, Any] = {"route": route, "json": json}
        self.ratelimited = True

        self.logger.debug("Waiting for ratelimit... Releasing a request after: %ss", retry_after)

        await sleep(retry_after)
        self.ratelimited = False

        self.logger.debug("Releasing a request.")

        return await self.http.request(
            **request
        )


class RequestManager:
    """
    RequestManager helping HTTP client. It handles configured delays, ratelimit and error handling.

    Parameters
    ----------
    http:
        HTTP Client.
    ratelimit_delay:
        Additional ratelimit delay, which is added when you reach ratelimit.
    request_delay:
        Delay between sending requests to rest api.

    Attributes
    ----------
    handler:
        ContextHandler object to handle ratelimit and errors.
    additional_delay:
        Additional ratelimit delay, which is added when you reach ratelimit.
    request_delay:
        Delay between sending requests to rest api.
    """
    __slots__ = ("handler", "additional_delay", "request_delay", "logger")

    def __init__(self, http: HTTPClient, ratelimit_delay: float, request_delay: float) -> None:
        self.handler: ContextHandler = ContextHandler(http=http, additional_delay=ratelimit_delay)

        self.additional_delay: float = ratelimit_delay
        self.request_delay: float = request_delay

    async def __aenter__(self) -> ContextHandler:
        """
        Method to return ContextHandler and wait request delay.

        Raises
        ------
        RuntimeError
            HTTP Session is not running.
        """
        if self.handler.http.session_status is False:
            raise RuntimeError("The request method was called without a working Session.")

        await sleep(self.request_delay)
        return self.handler

    async def __aexit__(self, exc_type, exc, tb) -> None:
        return None
