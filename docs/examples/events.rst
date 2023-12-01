Events Example
===============

.. code-block:: python
   :caption: simple_events.py
   :linenos:

   from pynext import PynextClient, SelfBot, GuildMessage, PrivateMessage
   from typing import Union

   client = PynextClient()

   @client.gateway.event('on_user_ready')
   async def on_ready(user: SelfBot):
      print(f"Selfbot: {user.username} is ready!")


   @client.gateway.event('on_message_create')
   async def on_message(user: SelfBot, message: Union[GuildMessage, PrivateMessage]):
       print(f"{user.username} received an event on_message!")
       print(message.content)

   client.run('TOKEN_1', 'TOKEN_2')

.. code-block:: python
   :caption: class_events.py
   :linenos:

   from pynext import PynextClient, SelfBot, GuildMessage, PrivateMessage
   from typing import Union

   class Client(PynextClient):
      async def on_user_ready(self, user: SelfBot):
         print(f"Selfbot: {user.username} is ready!")

      async def on_message(self, user: SelfBot, message: Union[GuildMessage, PrivateMessage]):
         print(f"{user.username} received an event on_message!")
         print(message.content)


   client = Client()
   client.run('TOKEN_1', 'TOKEN_2')
