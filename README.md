## Pynext - Discord API Wrapper for Discord selfbots.
> ⚠️ Project only for educational purposes!

> ⚠️ Project is still under development. It may contain bugs, and future updates will bring breaking changes.

![License](https://img.shields.io/github/license/xXenvy/Pynext?style=for-the-badge&color=%2315b328)
![PyPI - Downloads](https://img.shields.io/pypi/dm/pynext?style=for-the-badge&color=%2315b328)
![GitHub commit activity](https://img.shields.io/github/commit-activity/t/xXenvy/Pynext?style=for-the-badge&color=%2315b328)
![GitHub last commit (branch)](https://img.shields.io/github/last-commit/xXenvy/Pynext/master?style=for-the-badge&color=%2315b328)

# 💢 Requirements
> Python 3.9 or newer

# 🔧 Pynext Features
- Modern Pythonic API using `async` and `await`
- Proper rate limit handling
- Optimised in both `speed` and `memory`
- Properly typehinted
- Support for multiple accounts.

# 🛠️ Installation
```shell
pip install -U pynext
```
# 💫 Example
**See more examples on github:** [JUMP!](https://github.com/xXenvy/pynext/tree/master/examples)
```py
from pynext import PynextClient, SelfBot

client = PynextClient()

@client.gateway.event('on_user_ready')
async def on_ready(user: SelfBot):
    print(f"Selfbot: {user.username} is ready!")

client.run("TOKEN_1", "TOKEN_2")
```
