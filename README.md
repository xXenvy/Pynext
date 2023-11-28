## Pynext - Discord API Wrapper for Discord selfbots.
> ⚠️ Project only for educational purposes!
> 
![License](https://img.shields.io/github/license/xXenvy/AsyncCore?style=for-the-badge&color=%2315b328)
![PyPI - Downloads](https://img.shields.io/pypi/dm/AsyncCore?style=for-the-badge&color=%2315b328)
![GitHub commit activity](https://img.shields.io/github/commit-activity/t/xXenvy/AsyncCore?style=for-the-badge&color=%2315b328)
![GitHub last commit (branch)](https://img.shields.io/github/last-commit/xXenvy/AsyncCore/master?style=for-the-badge&color=%2315b328)

# 💢 Requirements
> Python 3.9 or newer

# 🔧 Pynext Features
- Modern Pythonic API using `async` and `await`
- Proper rate limit handling
- Optimised in both `speed` and `memory`
- Properly typehinted

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
