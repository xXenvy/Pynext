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
from typing import TYPE_CHECKING, Any

from asyncio import Event

from .types import Authorization
from .discord import Guild, VoiceChannel, DMChannel, DiscordUser, PresenceBuilder

from .errors import WebsocketNotConnected
from .state import State

if TYPE_CHECKING:
    from .rest import HTTPClient
    from .gateway import DiscordWebSocket


class SelfBot(DiscordUser):
    """
    Class representing the selfbot object.

    Parameters
    ----------
    token:
        Selfbot token needed to create authorization.
    user_data:
        Date received when logging into the account.
    http:
        HTTPClient needed to send requests.

    Attributes
    ----------
    gateway: :class:`DiscordWebSocket`
        SelfBot connection to the discord gateway.
    state: :class:`State`
        Helps creating new objects in fetch methods.
    authorization: :class:`Authorization`
        SelfBot authorization object.
    global_name: Optional[:class:`str`]
        SelfBot global name.
    username: :class:`str`
        SelfBot username.
    discriminator: :class:`str`
        SelfBot discriminator.
    id: :class:`int`
        SelfBot unique ID.
    email: :class:`str`
        Specifies if the user's email is verified.
    avatar_id: Optional[:class:`str`]
        ID of the user avatar.
    mfa_enabled: :class:`bool`
        Specifies if the user has MFA turned on.
    locale: :class:`str`
        The IETF language tag used to identify the language the user is using.
    premium_type: Optional[:class:`int`]
        Type of Nitro subscription on a user's account.
    """

    __slots__ = (
        "gateway",
        "state",
        "authorization",
        "mfa_enabled",
        "email",
        "verified",
        "locale",
        "premium_type",
        "_guilds",
        "_voice_states",
        "_dm_channels",
        "_users",
        "_ready",
    )

    def __init__(self, token: str, user_data: dict[str, Any], http: HTTPClient) -> None:
        super().__init__(state=State(http=http), user_data=user_data)

        self.state: State = (
            self._state
        )  # The state for the selfbot should be public, I think.
        self.gateway: DiscordWebSocket | None = None
        self.authorization: Authorization[str] = Authorization(token)

        self.email: str = user_data["email"]
        self.verified: bool = user_data["verified"]

        self.mfa_enabled: bool = user_data["mfa_enabled"]
        self.locale: str = user_data["locale"]
        self.premium_type: int | None = user_data["premium_type"]

        self._guilds: dict[int, Guild] = {}
        self._voice_states: dict[Guild, VoiceChannel] = {}
        self._dm_channels: dict[int, DMChannel] = {}
        self._users: dict[int, DiscordUser] = {}
        self._ready: Event = Event()

    def __repr__(self) -> str:
        return f"<SelfBot(global_name={self.global_name}, id={self.id})>"

    @property
    def http(self) -> HTTPClient:
        """
        Returns the global HTTPClient.
        """
        return self.state.http

    @property
    def token(self) -> str:
        """
        Selfbot authorization token.
        """
        return self.authorization.key

    @property
    def latency(self) -> float:
        """
        Websocket latency value. (Multiply by 1000 to get the value in milliseconds).
        Contain a value 0.0 if the websocket is not yet connected or didn't receive HEARTBEAT_ACK.
        """
        if self.gateway is None:
            # Websocket is not connected yet.
            return 0.0

        return self.gateway.latency

    @property
    def guilds(self) -> list[Guild]:
        """
        List of servers on which selfbot is available.

        .. note::
            If ``chunk_guilds`` in the :class:`PynextClient` is set to False, the list will be empty.

            You can call the :func:`fetch_guild` method to fetch guild object.
        """
        return list(self._guilds.values())

    @property
    def voice_states(self) -> dict[Guild, VoiceChannel]:
        """
        Voice states the selfbot is on.
        """
        return self._voice_states

    @property
    def dm_channels(self) -> list[DMChannel]:
        """
        List with dm selfbot channels.
        """
        return list(self._dm_channels.values())

    @property
    def users(self) -> list[DiscordUser]:
        """
        A list of discord users that the selfbot has access to.
        """
        return list(self._users.values())

    def is_ready(self) -> bool:
        """
        Whether selfbot is ready.
        """
        return self._ready.is_set()

    async def wait_until_ready(self) -> None:
        """
        Method waits until the selfbot will be ready.
        """
        await self._ready.wait()

    def get_voice_state(self, guild: Guild) -> VoiceChannel | None:
        """
        A method that returns voice state from the specified guild.

        Parameters
        ----------
        guild:
            guild object.
        """
        return self._voice_states.get(guild)

    def get_guild(self, guild_id: int) -> Guild | None:
        """
        Method to get guild from cache by id.

        Parameters
        ----------
        guild_id:
            Id of the guild we want to get.
        """
        return self._guilds.get(guild_id)

    def get_dm_channel(self, channel_id: int) -> DMChannel | None:
        """
        Method to get dm_channel from cache by id.

        Parameters
        ----------
        channel_id:
            Id of the channel we want to get.
        """
        return self._dm_channels.get(channel_id)

    def get_user(self, user_id: int) -> DiscordUser | None:
        """
        Method to get user from cache by id.

        Parameters
        ----------
        user_id:
            Id of the user we want to get.
        """
        return self._users.get(user_id)

    def get_application(self, application_id: int) -> Application | None:
        """
        Method to get application from cache by id.

        Parameters
        ----------
        application_id:
            Id of the application.
        """
        return self._applications.get(application_id)

    async def fetch_guild(self, guild_id: int) -> Guild:
        """
        Method to fetch the guild by id.

        .. note::
            This method will make the api request.
            Consider using :func:`get_guild` if you have chunked guilds.

        Parameters
        ----------
        guild_id:
            Id of the guild we want to get.

        Raises
        ------
        HTTPTimeoutError
            Request reached http timeout limit.
        NotFound
            Guild was not found.
        Forbidden
            Selfbot can't access that guild.
        HTTPException
            Fetching a guild failed.
        """
        data: dict[str, Any] = await self.http.fetch_guild(user=self, guild_id=guild_id)
        data["channels"] = await self.http.fetch_channels(user=self, guild_id=guild_id)

        guild: Guild = await self.state.create_guild(user=self, guild_data=data)

        self._add_guild(guild)
        return guild

    async def fetch_user(self, user_id: int) -> DiscordUser:
        """
        Method to fetch the user by id.

        .. note::
            This method will make the api request.

        Parameters
        ----------
        user_id:
            Id of the user we want to get.

        Raises
        ------
        HTTPTimeoutError
            Request reached http timeout limit.
        NotFound
            User not found.
        Forbidden
            Selfbot can't access that user.
        HTTPException
            Fetching a user failed.
        """
        data: dict[str, Any] = await self.http.fetch_user(user=self, user_id=user_id)
        user: DiscordUser = self.state.create_user(data=data)

        self._add_user(user)
        return user

    async def fetch_dm_channel(self, channel_id: int) -> DMChannel:
        """
        Method to fetch the dm channel by id.

        .. note::
            This method will make a api request.

        Parameters
        ----------
        channel_id:
            Id of the channel we want to get.

        Raises
        ------
        HTTPTimeoutError
            Request reached http timeout limit.
        NotFound
            Dm channel not found.
        Forbidden
            Selfbot can't access that channel.
        HTTPException
            Fetching a channel failed.
        """
        data: dict[str, Any] = await self.http.fetch_channel(
            user=self, channel_id=channel_id
        )
        channel: DMChannel = self.state.create_dm_channel(data=data)
        self._add_dm_channel(channel)

        return channel

    async def change_presence(self, presence: PresenceBuilder):
        """
        Method to update selfbot presence.

        Parameters
        ----------
        presence:
            PresenceBuilder object.

        Raises
        ------
        WebsocketNotConnected
            Selfbot has not connection to the gateway.
        """
        if not self.gateway or not self.gateway.websocket_status:
            raise WebsocketNotConnected(
                f"SelfBot: {self} has no connection to the gateway."
            )

        await self.gateway.change_presence(presence.to_dict())

    def _update_voice_state(self, guild: Guild, state: VoiceChannel | None) -> None:
        if state is None:
            try:
                del self._voice_states[guild]
            except KeyError:
                pass
        else:
            self._voice_states[guild] = state

    def _add_guild(self, guild: Guild) -> None:
        self._guilds[guild.id] = guild

    def _remove_guild(self, guild_id: int) -> None:
        try:
            del self._guilds[guild_id]
        except KeyError:
            pass

    def _add_dm_channel(self, channel: DMChannel) -> None:
        self._dm_channels[channel.id] = channel

    def _add_user(self, user: DiscordUser) -> None:
        self._users[user.id] = user
