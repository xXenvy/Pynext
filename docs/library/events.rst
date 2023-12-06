.. currentmodule:: pynext

Events
======
Documentation of all available library events. See how to use them: :ref:`Events Example`

.. function:: on_user_login(selfbot)

    Called when the selfbot object is properly created.

    However, this does not mean that the selfbot has made a connection to the discord gateway.

    :param selfbot: Selfbot, which just logged in.
    :type selfbot: :class:`SelfBot`

.. function:: on_user_ready(selfbot)

    Called when the selfbot connects to the gateway and completes chunking.

    :param selfbot: Selfbot that is ready.
    :type selfbot: :class:`SelfBot`

.. function:: on_channel_create(selfbot, channel)

    Called when a channel has been created.

    :param selfbot: Selfbot that received an event from the websocket.
    :type selfbot: :class:`SelfBot`
    :param channel: Created channel.
    :type channel: Union[:class:`GuildChannel`, :class:`DMChannel`]

.. function:: on_channel_edit(selfbot, old, new)

    Called when a channel has been edited.

    .. note::
        If the channel is not found in the internal cache, then this event will not be called.

    :param selfbot: Selfbot that received an event from the websocket.
    :type selfbot: :class:`SelfBot`
    :param old: Old channel object.
    :type old: Union[:class:`GuildChannel`, :class:`DMChannel`]
    :param new: New channel object.
    :type new: Union[:class:`GuildChannel`, :class:`DMChannel`]

.. function:: on_channel_delete(selfbot, channel)

    Called when a channel has been deleted.

    .. note::
        If the channel is not found in the internal cache, then this event will not be called.

    :param selfbot: Selfbot that received an event from the websocket.
    :type selfbot: :class:`SelfBot`
    :param channel: Deleted channel.
    :type channel: Union[:class:`GuildChannel`, :class:`DMChannel`]

.. function:: on_message_create(selfbot, message)

    Called when a Message is created and sent.

    :param selfbot: Selfbot that received an event from the websocket.
    :type selfbot: :class:`SelfBot`
    :param message: Received message.
    :type message: Union[:class:`GuildMessage`, :class:`PrivateMessage`]

.. function:: on_message_edit(selfbot, old, new)

    Called when the message has been edited.

    .. note::
        If old message is not found in the internal cache, then this event will not be called.

    :param selfbot: Selfbot that received an event from the websocket.
    :type selfbot: :class:`SelfBot`
    :param old: Old message object.
    :type old: Union[:class:`GuildMessage`, :class:`PrivateMessage`]
    :param new: New message object.
    :type new: Union[:class:`GuildMessage`, :class:`PrivateMessage`]

.. function:: on_message_delete(selfbot, message)

    Called when a message has been deleted.

    .. note::
        If the message is not found in the internal cache, then this event will not be called.

    :param selfbot: Selfbot that received an event from the websocket.
    :type selfbot: :class:`SelfBot`
    :param message: Deleted message.
    :type message: Union[:class:`GuildMessage`, :class:`PrivateMessage`]

.. function:: on_message_reaction_add(selfbot, reaction)

    Called when a reaction is added to a message.

    :param selfbot: Selfbot that received an event from the websocket.
    :type selfbot: :class:`SelfBot`
    :param reaction: Added reaction.
    :type reaction: :class:`MessageReaction`

.. function:: on_message_reaction_remove(selfbot, reaction)

    Called when the reaction is removed from the message.

    :param selfbot: Selfbot that received an event from the websocket.
    :type selfbot: :class:`SelfBot`
    :param reaction: Removed reaction.
    :type reaction: :class:`MessageReaction`

.. function:: on_guild_create(selfbot, guild)

    Called when Guild became available, or selfbot joined a new guild.

    :param selfbot: Selfbot that received an event from the websocket.
    :type selfbot: :class:`SelfBot`
    :param guild: Guild object.
    :type guild: :class:`Guild`

.. function:: on_guild_edit(selfbot, old, new)

    Called when guild will be updated.

    .. note::
        If the Guild is not found in the internal cache, then this event will not be called.

    :param selfbot: Selfbot that received an event from the websocket.
    :type selfbot: :class:`SelfBot`
    :param old: Old guild object.
    :type old: :class:`Guild`
    :param new: New guild object.
    :type new: :class:`Guild`

.. function:: on_guild_delete(selfbot, guild)

    Called when a guild has been deleted or selfbot left/was removed from a guild.

    .. note::
        If the Guild is not found in the internal cache, then this event will not be called.

    :param selfbot: Selfbot that received an event from the websocket.
    :type selfbot: :class:`SelfBot`
    :param guild: Deleted guild.
    :type guild: :class:`Guild`

.. function:: on_guild_emojis_update(selfbot, payload)

    Called when guild emojis will be updated.

    .. note::
        If the Guild is not found in the internal cache, then this event will not be called.

    :param selfbot: Selfbot that received an event from the websocket.
    :type selfbot: :class:`SelfBot`
    :param payload: Emojis payload.
    :type payload: :class:`EmojisUpdatePayload`

.. function:: on_member_update(selfbot, old, new)

    Called when GuildMember was updated.

    .. note::
        If the Guild / Member is not found in the internal cache, then this event will not be called.

    :param selfbot: Selfbot that received an event from the websocket.
    :type selfbot: :class:`SelfBot`
    :param old: Old guild member.
    :type old: :class:`GuildMember`
    :param new: New guild member.
    :type new: :class:`GuildMember`

.. function:: on_guild_ban_create(selfbot, banentry)

    Called when User was banned from a guild.

    :param selfbot: Selfbot that received an event from the websocket.
    :type selfbot: :class:`SelfBot`
    :param banentry: BanEntry object.
    :type banentry: :class:`BanEntry`

.. function:: on_guild_ban_create(selfbot, banentry)

    Called when User was unbanned from a guild.

    :param selfbot: Selfbot that received an event from the websocket.
    :type selfbot: :class:`SelfBot`
    :param banentry: Removed BanEntry object.
    :type banentry: :class:`BanEntry`

.. function:: on_guild_role_create(selfbot, role)

    Called when someone create a role on the guild.

    :param selfbot: Selfbot that received an event from the websocket.
    :type selfbot: :class:`SelfBot`
    :param role: Created role.
    :type role: :class:`Role`

.. function:: on_guild_role_update(selfbot, old, new)

    Called when someone updates a guild role.

    .. note::
        If the Guild / Role is not found in the internal cache, then this event will not be called.

    :param selfbot: Selfbot that received an event from the websocket.
    :type selfbot: :class:`SelfBot`
    :param old: Old role object.
    :type old: :class:`Role`
    :param new: New role object.
    :type new: :class:`Role`

.. function:: on_guild_role_delete(selfbot, role)

    Called when someone delete a role on the guild.

    .. note::
        If the Guild is not found in the internal cache, then this event will not be called.

    :param selfbot: Selfbot that received an event from the websocket.
    :type selfbot: :class:`SelfBot`
    :param role: Deleted role.
    :type role: :class:`Role`

.. function:: oo_interaction_create(selfbot, payload)

    Called when the selfbot will create interaction with the application.

    .. versionadded:: 1.0.6

    :param selfbot: Selfbot that received an event from the websocket.
    :type selfbot: :class:`SelfBot`
    :param payload: Interaction Payload.
    :type payload: :class:`InteractionPayload`

.. function:: oo_interaction_success(selfbot, payload)

    Called when the application will respond correctly to interaction.

    .. versionadded:: 1.0.6

    :param selfbot: Selfbot that received an event from the websocket.
    :type selfbot: :class:`SelfBot`
    :param payload: Interaction Payload.
    :type payload: :class:`InteractionPayload`

.. function:: oo_interaction_failure(selfbot, payload)

    Called when the application will not respond to interaction.

    .. versionadded:: 1.0.6

    :param selfbot: Selfbot that received an event from the websocket.
    :type selfbot: :class:`SelfBot`
    :param payload: Interaction Payload.
    :type payload: :class:`InteractionPayload`

.. function:: on_http_ratelimit(payload)

    Called when the HTTP client reaches ratelimit.

    :param payload: Ratelimit Payload.
    :type payload: :class:`RatelimitPayload`

.. function:: on_websocket_raw_receive(response)

    Called when websocket receives a gateway response.

    .. note::
        Event is called only when the ``debug_events`` parameter is enabled in the :class:`PynextClient` class.

    :param response: Raw gateway respo
    :type response: :class:`GatewayResponse`
