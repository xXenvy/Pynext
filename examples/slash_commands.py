from typing import Optional
from pynext import PynextClient, SelfBot, Guild, Application, SlashCommand

client = PynextClient(chunk_guilds=False)


@client.dispatcher.listen("on_user_ready")
async def on_ready(user: SelfBot):
    print(f"Selfbot: {user.username} is ready!")

    guild: Guild = await user.fetch_guild(guild_id=123)
    general_chat = guild.get_channel(channel_id=123)

    if general_chat is None:
        raise RuntimeError("Chat not found :(")

    await guild.fetch_applications(user)

    app: Optional[Application] = guild.get_application(
        application_id=155149108183695360
    )  # Dyno bot id.
    if app is None:
        raise RuntimeError("Application not found.")

    command: Optional[SlashCommand] = app.get_command_by_name("addrole")
    if command is None:
        raise RuntimeError("Command not found.")

    await command.use(user=user, channel=general_chat, name="rolename123")
    # Argument name is used by slashcommand.


client.run("TOKEN_1", "TOKEN_2")
