from pynext import SelfBot, PynextClient, File
from aiohttp import ClientTimeout

client = PynextClient(chunk_guilds=False, http_timeout=ClientTimeout(30))
"""
By default pynext uses ClientTimeout(10) for http requests.

If you sending large files and you have slow internet connection you can get HTTPTimeoutError.
To avoid this, you can increase the timeout limit.
"""


@client.dispatcher.listen("on_user_ready")
async def on_ready(user: SelfBot):
    print(f"Selfbot: {user.username} is ready!")

    guild = await user.fetch_guild(123)
    channel = await guild.fetch_channel(user, 123)

    with open("../assets/discordlogo.png", "rb") as f:
        discord_logo_bytes: bytes = f.read()

    # We can provide the bytes of the file.
    discord_logo: File = File(discord_logo_bytes, "discordlogo.png")

    # Or we can provide the path to the file.
    # Library will automatically read the bytes from the file.
    discord_logo_2: File = File("../assets/discordlogo.png", "discordlogo_2.png")

    await channel.send(user, content="Hello!", files=[discord_logo_2, discord_logo])


client.run("TOKEN_1", "TOKEN_2")
