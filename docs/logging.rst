Logging
===============
A basic method of logging library logs.

.. warning::
   Logger at ``DEBUG`` level (default) shows authorization header.

.. code-block:: python
   :caption: logging.py
   :linenos:
   :emphasize-lines: 2, 5

   from pynext import PynextClient, SelfBot
   from pynext.debug import DebugLogger

   client = PynextClient()
   DebugLogger.run(file_path='logs.log')

   @client.gateway.event('on_user_ready')
   async def on_ready(user: SelfBot):
      print(f"Selfbot: {user.username} is ready!")

   client.run('TOKEN_1', 'TOKEN_2')
