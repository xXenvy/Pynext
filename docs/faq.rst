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

Currently, the library does not support this, but there is work in progress to introduce it as soon as possible.
