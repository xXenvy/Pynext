from typing import Union

from pynext import PynextClient, SelfBot, GuildMessage, PrivateMessage

"""
There are two main ways to handle events.

The first one:
"""
client = PynextClient()


@client.dispatcher.listen("on_user_ready")
async def on_ready(user: SelfBot):
    print(f"Selfbot: {user.username} is ready!")


@client.dispatcher.listen("on_message_create")
async def on_message(user: SelfBot, message: Union[GuildMessage, PrivateMessage]):
    print(f"{user.username} received an event on_message!")
    print(message.content)


client.run("TOKEN")


# The second way:


class Client(PynextClient):
    async def on_user_ready(self, user: SelfBot):
        print(f"Selfbot: {user.username} is ready!")

    async def on_message(
        self, user: SelfBot, message: Union[GuildMessage, PrivateMessage]
    ):
        print(f"{user.username} received an event on_message!")
        print(message.content)


client = Client()
client.run("TOKEN")
