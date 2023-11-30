<div align="center">

  <img alt="" src="assets/discordlogo.png" width="200px"/>
  
  ## Pynext - Discord API Wrapper for selfbots.
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
**See more examples on github:** [JUMP!](https://github.com/xXenvy/pynext/tree/master/examples)
```py
import pynext

client = pynext.PynextClient(chunk_guilds=False)

@client.gateway.event('on_user_ready')
async def on_ready(user: pynext.SelfBot):
    print("User: {} is ready!".format(user))

    guild: pynext.Guild = await user.fetch_guild(guild_id=123)
    await guild.owner.send(user, content='Hello owner!')


client.run('TOKEN_1', 'TOKEN_2')
```

# 📃 Todo
- [x] Support for multiple accounts.
- [ ] Discord connection support on the voice channel.
- [ ] Slash commands and other interaction stuff handling.
