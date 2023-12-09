.. currentmodule:: pynext

Faq
===
Frequently Asked Questions.

**Can i get ban for using this library?**

Yes. Using programs / libraries for selfbotting is forbidden by Discord ToS. Using this library, you must expect that you may get banned.


**Library takes an extremely long time to start up.**

If the client takes a long time to start or doesn't start at all,
it may mean that the selfbot has too many servers, channels and users to chunk.
To prevent this, disable ``chunk_guilds`` in the :class:`PynextClient` class.

.. note::
  If you disable guilds chunking then selfbot will not be able to access servers via :attr:`SelfBot.guilds`.

  You will have to use the :func:`SelfBot.fetch_guild` method, which makes a request to the API.

**Does the library support the use of buttons / slashcommands?**

Library currently supports only slashcommands. The other things are being worked on.


**How to get a "user / selfbot" token?**

This can be done in a couple of ways. Two of the easier ways you can find here:
`Article 1, <https://pcstrike.com/how-to-get-discord-token/>`_
`Article 2. <https://www.geeksforgeeks.org/how-to-get-discord-token/>`_

.. note::
    Token resets every time you log in / log out of your account.

    If you want to acquire the token from several accounts, you will have to log in to the account via the "incognito" card,
    then acquire the token and close the incognito card, and then repeat this process for the next account.