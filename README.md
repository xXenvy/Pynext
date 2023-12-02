<div align="center">

  <img alt="" src="assets/discordlogo.png" width="200px"/>

  ## Pynext - Discord API Wrapper for selfbots written from scratch in Python.
  `⚠️ Project only for educational purposes!`

  `⚠️ Project is still under development. It may contain bugs, and future updates will bring breaking changes.`

![License](https://img.shields.io/github/license/xXenvy/Pynext?style=for-the-badge&color=%2315b328)
![PyPI - Downloads](https://img.shields.io/pypi/dm/pynext?style=for-the-badge&color=%2315b328)
![GitHub commit activity](https://img.shields.io/github/commit-activity/t/xXenvy/Pynext?style=for-the-badge&color=%2315b328)
![GitHub last commit (branch)](https://img.shields.io/github/last-commit/xXenvy/Pynext/master?style=for-the-badge&color=%2315b328)
</div>

# 💢 Requirements
> Python 3.9 or newer

# 🔧 Pynext Features
- Modern Pythonic API using `async` and `await`.
- Proper rate limit handling.
- Optimised in both `speed` and `memory`.
- Properly typehinted.
- Support for multiple accounts.

# 🛠️ Installation
```shell
pip install -U pynext
```
# 💫 Example
**See more examples on:** [Github](https://github.com/xXenvy/pynext/tree/master/examples) or [Docs](https://pynext.readthedocs.io/en/latest/examples/).
```py
from pynext import PynextClient, SelfBot, GuildMessage, PrivateMessage
from typing import Union

client = PynextClient(chunk_guilds=False)

@client.gateway.event('on_user_ready')
async def on_ready(user: SelfBot):
    print("User: {} is ready!".format(user))


@client.gateway.event('on_message_create')
async def on_message(selfbot: SelfBot, message: Union[PrivateMessage, GuildMessage]):
    if message.content == "?ping" and message.author_id == selfbot.id:
        await message.reply(selfbot, content=f"**Pong!** {round(selfbot.latency * 1000)}ms")

client.run("TOKEN_1", "TOKEN_2")

```
# 🧷 Links
- [Documentation](https://pynext.readthedocs.io/en/latest/)
- [Report a bug or feature](https://github.com/xXenvy/pynext/issues/new/choose)

# 📃 Todo
- [x] Support for multiple accounts.
- [ ] Discord connection support on the voice channel.
- [ ] Slash commands and other interaction stuff handling.
