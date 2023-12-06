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
from typing import TYPE_CHECKING, ClassVar, Any

from aiohttp import (
    ClientSession,
    ClientResponse,
    ClientTimeout,
    ClientWebSocketResponse,
)
from logging import getLogger, Logger
from asyncio import get_event_loop, TimeoutError

from ..errors import Unauthorized, HTTPTimeoutError
from ..types import Authorization, MessageReference, OverwritePayload, RatelimitPayload
from ..discord import Permissions, Role, GuildMember

from .route import Route
from .manager import RequestManager

if TYPE_CHECKING:
    from datetime import datetime

    from ..selfbot import SelfBot
    from ..gateway import Dispatcher


class HTTPClient:
    """
    HTTP client functionality representation.

    Parameters
    ----------
    request_delay:
        Delay between sending requests to rest api.
    ratelimit_delay:
        Additional ratelimit delay, which is added when you reach ratelimit.
    dispatcher:
        Dispatcher to call the HTTP Ratelimit event.
    timeout:
        Parameter to manage HTTP connection timeout.
    """

    __slots__ = (
        "_state",
        "_dispatcher",
        "_logger",
        "_session",
        "_manager",
        "_request_delay",
        "_timeout",
    )
    __version__: ClassVar[str] = "1.0.3"

    BASE_URL: ClassVar[str] = "https://discord.com/api/v10/"

    def __init__(
        self,
        request_delay: float,
        ratelimit_delay: float,
        dispatcher: Dispatcher,
        timeout: ClientTimeout,
    ):
        self._session: ClientSession | None = None
        self._dispatcher: Dispatcher = dispatcher

        self._request_delay: float = request_delay
        self._logger: Logger = getLogger("pynext.rest")

        self._timeout: ClientTimeout = timeout
        self._manager: RequestManager = RequestManager(
            http=self, ratelimit_delay=ratelimit_delay, request_delay=request_delay
        )

    def __repr__(self) -> str:
        return f"<HTTPClient(status={self.session_status})>"

    def __del__(self):
        get_event_loop().run_until_complete(self.close())

    @property
    def default_headers(self) -> dict[str, str]:
        """
        Default headers used for HTTP requests.
        """
        return {
            "SelfBot-Agent": f"Pynext HTTP (v{self.__version__})",
            "Accept": "*/*",
            "authority": "discord.com",
            "Origin": "https://discord.com",
        }

    @property
    def request_delay(self) -> float:
        """
        Specified delay between requests.
        """
        return self._manager.request_delay

    @property
    def ratelimit_delay(self) -> float:
        """
        Specified additional ratelimit delay.
        """
        return self._manager.additional_delay

    @property
    def session_status(self) -> bool:
        """
        Whether the http session is working.
        """
        return (
            not self._session.closed
            if isinstance(self._session, ClientSession)
            else False
        )

    @property
    def timeout(self) -> ClientTimeout:
        """
        Specified ClientTimeout.
        """
        return self._timeout

    async def connect_to_gateway(self, url: str) -> ClientWebSocketResponse:
        """
        Method for connecting to a gateway.

        Parameters
        ----------
        url:
            url to connect.

        Raises
        ------
        :exc:`RuntimeError`
            HTTP Session is not running.
        """
        if self.session_status is False:
            raise RuntimeError(
                "Connecting to gateway cannot be done without a working session."
            )

        assert isinstance(self._session, ClientSession)
        return await self._session.ws_connect(url=url, headers=self.default_headers)

    async def setup(self) -> None:
        """
        Method to setup HTTP session.
        """
        self._session = ClientSession(timeout=self._timeout)
        self._logger.info("HTTP Session has been created.")

    async def close(self) -> None:
        """
        Method to close HTTP session.
        """
        if isinstance(self._session, ClientSession):
            self._logger.info("Closing session...")
            await self._session.close()

    async def request(
        self,
        route: Route,
        json: dict[str, Any] | None = None,
        user: SelfBot | None = None,
    ) -> ClientResponse:
        """
        A method for sending HTTP requests.

        Parameters
        ----------
        route:
            Request route.
        json:
            Json request data.
        user:
            SelfBot to identify ratelimit.

        Raises
        ------
        RuntimeError
            HTTP Session is not defined.
        HTTPTimeoutError
            Request reached http timeout limit.
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
        async with self._manager as request_manager:
            assert isinstance(self._session, ClientSession)

            headers: dict[str, str] = {**self.default_headers, **route.headers}
            url: str = self.BASE_URL + route.url

            self._logger.debug(f"Sending request: {route} | {route.headers}")

            try:
                response: ClientResponse = await self._session.request(
                    method=route.method, url=url, headers=headers, json=json
                )
            except TimeoutError:
                raise HTTPTimeoutError(f"Reached timeout limit under route: {route}")

            if request_manager.is_ratelimited(response):
                data: dict = await response.json()
                retry_after: float = data["retry_after"]
                global_ratelimit: bool = data.get("global", False)

                self._logger.debug(
                    f"Ratelimit reached. Retry after: {retry_after} |"
                    f" global: {global_ratelimit}. Under route: {route}."
                )

                self._dispatcher.dispatch(
                    "on_http_ratelimit",
                    RatelimitPayload(
                        retry_after=retry_after,
                        is_global=global_ratelimit,
                        route=route,
                        user=user,
                    ),
                )

                response: ClientResponse = await request_manager.handle_ratelimit(
                    retry_after, route, json
                )

            await request_manager.handle_errors(response)
            return response

    async def get_image_bytes(self, url: str) -> bytes:
        """
        HTTP request to get image bytes.

        Parameters
        ----------
        url:
            image url.
        """
        route: Route = Route(method="GET", url=url)
        response: ClientResponse = await self.request(route)
        return await response.read()

    async def login_request(self, token: str) -> None | dict[str, Any]:
        """
        HTTP Request to check the token and obtain account data.

        Parameters
        ----------
        token:
            Selfbot token.
        """
        auth: Authorization = Authorization(key=token)
        route: Route = Route(method="GET", url="users/@me", headers=auth.headers)

        try:
            response: ClientResponse = await self.request(route)
        except Unauthorized:
            return

        return await response.json()

    async def fetch_user(self, user: SelfBot, user_id: int) -> dict[str, Any]:
        """
        HTTP request that fetches a specified user.

        Parameters
        ----------
        user:
            Selfbot to make the request.
        user_id:
            SelfBot id to fetch.
        """
        route = Route(
            method="GET",
            url="users/{user_id}",
            user_id=user_id,
            headers=user.authorization.headers,
        )
        response: ClientResponse = await self.request(route, user=user)
        return await response.json()

    async def create_dm(self, user: SelfBot, user_id: int) -> dict[str, Any]:
        """
        HTTP request that creates a dm channel.

        Parameters
        ----------
        user:
            Selfbot to make the request.
        user_id:
            User id to create a dm channel.
        """
        route = Route(
            method="POST",
            url="users/@me/channels",
            user_id=user_id,
            headers=user.authorization.headers,
        )

        response: ClientResponse = await self.request(
            route, json={"recipient_id": user_id}, user=user
        )
        return await response.json()

    async def send_friend_request(self, user: SelfBot, user_id: int) -> None:
        """
        HTTP request that sends a friend invite.

        Parameters
        ----------
        user:
            Selfbot to make the request.
        user_id:
            SelfBot id to create a dm channel.
        """
        route = Route(
            method="PUT",
            url="users/@me/relationships/{user_id}",
            user_id=user_id,
            headers=user.authorization.headers,
        )
        await self.request(route, json={}, user=user)

    async def remove_friend(self, user: SelfBot, user_id: int) -> None:
        """
        HTTP request to remove a friend.

        Parameters
        ----------
        user:
            Selfbot to make the request.
        user_id:
            friend's id.
        """
        route = Route(
            method="DELETE",
            url="users/@me/relationships/{user_id}",
            user_id=user_id,
            headers=user.authorization.headers,
        )
        await self.request(route, user=user)

    async def fetch_guild(self, user: SelfBot, guild_id: int) -> dict[str, Any]:
        """
        HTTP request to fetch guild data.

        Parameters
        ----------
        user:
            Selfbot to make the request.
        guild_id:
            Id of the guild to fetch.
        """
        route = Route(
            method="GET",
            url="guilds/{guild_id}",
            guild_id=guild_id,
            headers=user.authorization.headers,
        )

        response: ClientResponse = await self.request(route, user=user)
        return await response.json()

    async def send_message(
        self,
        user: SelfBot,
        channel_id: int,
        message_content: str,
        message_reference: MessageReference | None = None,
        reply_mention: bool = True,
    ) -> dict[str, Any]:
        """
        HTTP request to send message.

        Parameters
        ----------
        user:
            Selfbot to make the request.
        channel_id:
            Id of the channel on which you want to send the message.
        message_content:
            Content of the message.
        message_reference:
            MessageReference data with details of which message you are responding to.
        reply_mention:
            Whether you want to mention the author when replying to a message.
        """

        route = Route(
            method="POST",
            url="channels/{channel_id}/messages",
            headers=user.authorization.headers,
            channel_id=channel_id,
        )

        payload: dict[str, Any] = {
            "content": message_content,
            "message_reference": message_reference,
        }

        if message_reference:
            payload["allowed_mentions"] = {"replied_user": reply_mention}

        response: ClientResponse = await self.request(route, payload, user)
        return await response.json()

    async def fetch_messages(
        self,
        user: SelfBot,
        channel_id: int,
        limit: int = 10,
        message_id: int | None = None,
    ) -> list[dict[str, Any]]:
        """
        HTTP request to fetch messages.

        Parameters
        ----------
        user:
            Selfbot to make the request.
        channel_id:
            id of the channel where you want to fetch messages.
        limit:
            Max number of messages to fetch.

            .. note::
                At one time, you can fetch a total of 100 messages.
        message_id:
            Get messages around this message ID.
        """
        url: str = f"channels/{channel_id}/messages?limit={limit}"

        if message_id:
            url += f"&around={message_id}"

        route = Route(
            method="GET",
            url=url,
            headers=user.authorization.headers,
            channel_id=channel_id,
        )

        response: ClientResponse = await self.request(route, user=user)
        return await response.json()

    async def delete_message(
        self, user: SelfBot, channel_id: int, message_id: int
    ) -> None:
        """
        HTTP request to delete message.

        Parameters
        ----------
        user:
            Selfbot to make the request.
        channel_id:
            id of the channel the message is on.
        message_id:
            message id to delete.
        """
        route = Route(
            method="DELETE",
            url="channels/{channel_id}/messages/{message_id}",
            headers=user.authorization.headers,
            channel_id=channel_id,
            message_id=message_id,
        )
        await self.request(route, user=user)

    async def edit_message(
        self, user: SelfBot, channel_id: int, message_id: int, content: str
    ) -> dict[str, Any]:
        """
        HTTP request to edit message.

        Parameters
        ----------
        user:
            Selfbot to make the request.
        channel_id:
            id of the channel the message is on.
        message_id:
            message id to edit.
        content:
            message content to edit.
        """
        route = Route(
            method="PATCH",
            url="channels/{channel_id}/messages/{message_id}",
            headers=user.authorization.headers,
            channel_id=channel_id,
            message_id=message_id,
        )

        response: ClientResponse = await self.request(
            route, json={"content": content}, user=user
        )

        return await response.json()

    async def fetch_guild_roles(
        self, user: SelfBot, guild_id: int
    ) -> list[dict[str, Any]]:
        """
        HTTP request to fetch guild roles.

        Parameters
        ----------
        user:
            Selfbot to make the request.
        guild_id:
            guild id to fetch roles.
        """
        route = Route(
            method="GET",
            url="guilds/{guild_id}/roles",
            guild_id=guild_id,
            headers=user.authorization.headers,
        )

        response: ClientResponse = await self.request(route, user=user)
        return await response.json()

    async def edit_role(
        self, user: SelfBot, guild_id: int, role: Role, params: dict[str, Any]
    ) -> dict[str, Any]:
        """
        HTTP request to edit role.

        Parameters
        ----------
        user:
            Selfbot to make the request.
        guild_id:
            id of the guild where the role is on.
        role:
            Role to edit.
        params:
            Parameters for editing the role.
        """
        route = Route(
            method="PATCH",
            url="guilds/{guild_id}/roles/{role_id}",
            guild_id=guild_id,
            role_id=role.id,
            headers=user.authorization.headers,
        )

        if isinstance(params.get("permissions"), Permissions):
            permissions: Permissions = params["permissions"]

            role.permissions = role.permissions.update(permissions)
            params["permissions"] = role.permissions.get_bitwise_by_flags()

        response: ClientResponse = await self.request(route, json=params, user=user)
        return await response.json()

    async def delete_role(self, user: SelfBot, guild_id: int, role_id: int) -> None:
        """
        HTTP request to delete role.

        Parameters
        ----------
        user:
            Selfbot to make the request.
        guild_id:
            Id of the guild where the role is on.
        role_id:
            Role id to delete.
        """
        route = Route(
            method="DELETE",
            url="guilds/{guild_id}/roles/{role_id}",
            guild_id=guild_id,
            role_id=role_id,
            headers=user.authorization.headers,
        )

        await self.request(route, user=user)

    async def fetch_channel(self, user: SelfBot, channel_id: int) -> dict[str, Any]:
        """
        HTTP request to fetch channel data.

        Parameters
        ----------
        user:
            Selfbot to make the request.
        channel_id:
            Id of the channel.
        """
        route = Route(
            method="GET",
            url="channels/{channel_id}",
            channel_id=channel_id,
            headers=user.authorization.headers,
        )

        response: ClientResponse = await self.request(route, user=user)
        return await response.json()

    async def fetch_channels(
        self, user: SelfBot, guild_id: int
    ) -> list[dict[str, Any]]:
        """
        HTTP request to guild channels.

        Parameters
        ----------
        user:
            Selfbot to make the request.
        guild_id:
            Guild id to fetch channels.
        """
        route = Route(
            method="GET",
            url="guilds/{guild_id}/channels",
            guild_id=guild_id,
            headers=user.authorization.headers,
        )

        response: ClientResponse = await self.request(route, user=user)
        return await response.json()

    async def edit_channel(
        self, user: SelfBot, channel_id: int, params: dict[str, Any]
    ) -> dict[str, Any]:
        """
        HTTP request to edit channel.

        Parameters
        ----------
        user:
            Selfbot to make the request.
        channel_id:
            Channel id to edit.
        params:
            parameters to edit the channel.
        """
        route = Route(
            method="PATCH",
            url="channels/{channel_id}",
            channel_id=channel_id,
            headers=user.authorization.headers,
        )

        if params.get("overwrites"):
            overwrites_payload: list[OverwritePayload] = []

            for overwrite_data in params["overwrites"]:
                for target, overwrite in overwrite_data.items():
                    overwrites_payload.append(
                        OverwritePayload(
                            id=target.id,
                            type=0 if isinstance(target, Role) else 1,
                            allow=str(overwrite.allow.key),
                            deny=str(overwrite.deny.key),
                        )
                    )

            del params["overwrites"]
            params["permission_overwrites"] = overwrites_payload

        response: ClientResponse = await self.request(route, json=params, user=user)
        return await response.json()

    async def delete_channel(self, user: SelfBot, channel_id: int) -> None:
        """
        HTTP request to delete channel.

        Parameters
        ----------
        user:
            Selfbot to make the request.
        channel_id:
            Channel id to delete.
        """
        route = Route(
            method="DELETE",
            url="channels/{channel_id}",
            channel_id=channel_id,
            headers=user.authorization.headers,
        )

        await self.request(route, user=user)

    async def fetch_member(
        self, user: SelfBot, guild_id: int, member_id: int
    ) -> dict[str, Any]:
        """
        HTTP request to fetch guild member.

        Parameters
        ----------
        user:
            Selfbot to make the request.
        guild_id:
            Id of the server on which the user is on.
        member_id:
            Member id to fetch.
        """
        route: Route = Route(
            method="GET",
            url="guilds/{guild_id}/members/{member_id}",
            guild_id=guild_id,
            member_id=member_id,
            headers=user.authorization.headers,
        )

        response: ClientResponse = await self.request(route, user=user)
        return await response.json()

    async def edit_member(
        self, user: SelfBot, guild_id: int, member: GuildMember, params: dict[str, Any]
    ) -> dict[str, Any]:
        """
        HTTP request to edit member.

        Parameters
        ----------
        user:
            Selfbot to make the request.
        guild_id:
            Id of the server on which the user is on.
        member:
            Member to edit.
        params:
            parameters to edit the member.
        """

        route: Route = Route(
            method="PATCH",
            url="guilds/{guild_id}/members/{member_id}",
            guild_id=guild_id,
            member_id=member.id,
            headers=user.authorization.headers,
        )
        member_roles: list[Role] = member.roles

        if params.get("roles_to_add") is not None:
            for role_to_add in params["roles_to_add"]:
                if role_to_add not in member_roles:
                    member_roles.append(role_to_add)

        if params.get("roles_to_remove") is not None:
            for role_to_remove in params["roles_to_remove"]:
                if role_to_remove in member_roles:
                    member_roles.remove(role_to_remove)

        try:
            time: datetime | None = params["communication_disabled_until"]
            if time:
                params["communication_disabled_until"] = time.isoformat()
        except KeyError:
            pass

        try:
            del params["roles_to_add"]
        except KeyError:
            pass

        try:
            del params["roles_to_remove"]
        except KeyError:
            pass

        try:
            channel_id: int | None = params["voice_channel_id"]
            del params["voice_channel_id"]

            if channel_id:
                params["channel_id"] = channel_id
        except KeyError:
            pass

        params["roles"] = [role.id for role in member_roles]

        if len(params["roles"]) <= 0:
            del params["roles"]

        response: ClientResponse = await self.request(route, json=params, user=user)
        return await response.json()

    async def fetch_user_profile(
        self, user: SelfBot, user_id: int, **settings: Any
    ) -> dict[str, Any]:
        """
        HTTP request to fetch member profile.

        Parameters
        ----------
        user:
            Selfbot to make the request.
        user_id:
            user id to fetch profile.
        settings:
            Settings for profile fetching.
        """
        url: str = "users/{user_id}/profile?"

        for key, value in settings.items():
            url += f"{key}={value}&"

        route: Route = Route(
            method="GET",
            url=url[:-1],
            user_id=user_id,
            headers=user.authorization.headers,
        )

        response: ClientResponse = await self.request(route, user=user)

        return await response.json()

    async def create_reaction(
        self, user: SelfBot, channel_id: int, message_id: int, emoji: str
    ) -> None:
        """
        HTTP request to add reaction to message.

        Parameters
        ----------
        user:
            Selfbot to make the request.
        channel_id:
            Id of the channel on which the message is.
        message_id:
            Id of the message.
        emoji:
            Emoji to add.
        """
        route: Route = Route(
            method="PUT",
            url="channels/{channel_id}/messages/{message_id}/reactions/{emoji}/@me",
            channel_id=channel_id,
            message_id=message_id,
            emoji=emoji,
            headers=user.authorization.headers,
        )
        await self.request(route, user=user)

    async def remove_reaction(
        self, user: SelfBot, channel_id: int, message_id: int, emoji: str, user_id: int
    ) -> None:
        """
        HTTP request to remove reaction from message.

        Parameters
        ----------
        user:
            Selfbot to make the request.
        channel_id:
            Id of the channel on which the message is.
        message_id:
            Id of the message.
        emoji:
            Emoji to remove.
        user_id:
            Id of reaction author.
        """
        route: Route = Route(
            method="DELETE",
            url="channels/{channel_id}/messages/{message_id}/reactions/{emoji}/{user_id}",
            channel_id=channel_id,
            message_id=message_id,
            emoji=emoji,
            user_id=user_id,
            headers=user.authorization.headers,
        )

        await self.request(route, user=user)

    async def remove_all_reactions(
        self, user: SelfBot, channel_id: int, message_id: int
    ) -> None:
        """
        HTTP request to remove all reactions from message.

        Parameters
        ----------
        user:
            Selfbot to make the request.
        channel_id:
            Id of the channel on which the message is.
        message_id:
            Id of the message.
        """
        route: Route = Route(
            method="DELETE",
            url="channels/{channel_id}/messages/{message_id}/reactions",
            channel_id=channel_id,
            message_id=message_id,
            headers=user.authorization.headers,
        )

        await self.request(route, user=user)

    async def get_reactions(
        self, user: SelfBot, channel_id: int, message_id: int, emoji: str
    ) -> list[dict[str, Any]]:
        """
        HTTP request to get all reactions from message.

        Parameters
        ----------
        user:
            Selfbot to make the request.
        channel_id:
            Id of the channel on which the message is.
        message_id:
            Id of the message.
        emoji:
            Reaction emoji.
        """
        route: Route = Route(
            method="GET",
            url="channels/{channel_id}/messages/{message_id}/reactions/{emoji}",
            channel_id=channel_id,
            message_id=message_id,
            emoji=emoji,
            headers=user.authorization.headers,
        )

        response: ClientResponse = await self.request(route, user=user)

        return await response.json()

    async def fetch_guild_ban(
        self, user: SelfBot, guild_id: int, user_id: int
    ) -> dict[str, Any]:
        """
        HTTP request to get ban data.

        Parameters
        ----------
        user:
            Selfbot to make the request.
        guild_id:
            Id of the guild on which the ban is.
        user_id:
            Id of the banned user.
        """
        route: Route = Route(
            method="GET",
            url=f"guilds/{guild_id}/bans/{user_id}",
            guild_id=guild_id,
            headers=user.authorization.headers,
        )

        response: ClientResponse = await self.request(route, user=user)

        return await response.json()

    async def fetch_guild_bans(
        self, user: SelfBot, guild_id: int, limit: int = 1000
    ) -> list[dict[str, Any]]:
        """
        HTTP request to fetch all guild bans.

        Parameters
        ----------
        user:
            Selfbot to make the request.
        guild_id:
            Id of the guild.
        limit:
            Limit of bans.
        """
        route: Route = Route(
            method="GET",
            url=f"guilds/{guild_id}/bans?limit={limit}",
            guild_id=guild_id,
            headers=user.authorization.headers,
        )

        response: ClientResponse = await self.request(route, user=user)

        return await response.json()

    async def send_typing(self, user: SelfBot, channel_id: int) -> None:
        """
        HTTP request to send typing on channel.

        Parameters
        ----------
        user:
            Selfbot to make the request.
        channel_id:
            Id of the channel.
        """
        route: Route = Route(
            method="POST",
            url="channels/{channel_id}/typing",
            channel_id=channel_id,
            headers=user.authorization.headers,
        )

        await self.request(route, user=user)

    async def create_role(
        self, user: SelfBot, guild_id: int, params: dict[str, Any]
    ) -> dict[str, Any]:
        """
        HTTP request to create guild role.

        Parameters
        ----------
        user:
            Selfbot to make the request.
        guild_id:
            Id of the guild.
        params:
            Role parameters.
        """
        route = Route(
            method="POST",
            url="guilds/{guild_id}/roles",
            guild_id=guild_id,
            headers=user.authorization.headers,
        )
        response: ClientResponse = await self.request(route, json=params, user=user)
        return await response.json()

    async def create_channel(
        self, user: SelfBot, guild_id: int, params: dict[str, Any]
    ) -> dict[str, Any]:
        """
        HTTP request to create guild channel.

        Parameters
        ----------
        user:
            Selfbot to make the request.
        guild_id:
            Id of the guild.
        params:
            Channel parameters.
        """
        route = Route(
            method="POST",
            url="guilds/{guild_id}/channels",
            guild_id=guild_id,
            headers=user.authorization.headers,
        )

        response: ClientResponse = await self.request(route, json=params, user=user)
        return await response.json()

    async def unack_message(
        self, user: SelfBot, channel_id: int, message_id: int
    ) -> None:
        """
        HTTP request to mark a message as unread.

        Parameters
        ----------
        user:
            Selfbot to make the request.
        channel_id:
            Id of the channel where the message is.
        message_id:
            Id of the message.
        """
        route = Route(
            method="POST",
            url="channels/{channel_id}/messages/{message_id}/ack",
            channel_id=channel_id,
            message_id=message_id,
            headers=user.authorization.headers,
        )

        payload: dict[str, bool | int] = {"manual": True, "mention_count": 0}

        await self.request(route, json=payload, user=user)

    async def fetch_applications(
        self, user: SelfBot, guild_id: int | None = None, channel_id: int | None = None
    ) -> dict[str, Any]:
        """
        HTTP request to fetch guild applications.

        .. versionadded:: 1.0.6

        Parameters
        ----------
        user:
            Selfbot to make the request.
        guild_id:
            Id of the guild.
        channel_id:
            Id of the dm channel.
        """
        if not guild_id and not channel_id:
            raise RuntimeError("Missing guild_id or channel_id parameter.")

        start_url: str = f"guilds/{guild_id}" if guild_id else f"channels/{channel_id}"

        route = Route(
            method="GET",
            url=f"{start_url}/application-command-index",
            headers=user.authorization.headers,
        )

        response: ClientResponse = await self.request(route, user=user)
        return await response.json()

    async def use_interaction(self, user: SelfBot, payload: dict[str, Any]) -> None:
        """
        HTTP request to send interaction.

        .. versionadded:: 1.0.6

        Parameters
        ----------
        user:
            Selfbot to make the request.
        payload:
            Interaction payload.
        """
        route = Route(
            method="POST",
            url="interactions",
            headers=user.authorization.headers,
        )
        await self.request(route, user=user, json=payload)
