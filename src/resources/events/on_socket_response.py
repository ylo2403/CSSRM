from ..structures.Bloxlink import Bloxlink # pylint: disable=import-error
from ..exceptions import CancelCommand # pylint: disable=import-error
from discord.utils import find
from discord import Member, User, DMChannel



handle_slash_command = Bloxlink.get_module("commands", attrs="handle_slash_command")

@Bloxlink.event
async def on_socket_response(msg):
    t = msg["t"]
    d = msg["d"]

    if t == "INTERACTION_CREATE":
        command_data = d["data"]
        command_name = command_data["name"]
        command_id   = command_data["id"]
        command_args = []

        subcommand = None

        if command_data.get("options"):
            for arg in command_data["options"]:
                if arg.get("value") is not None:
                    command_args.append([arg["name"], arg["value"]])
                else:
                    subcommand = arg["name"]

        interaction_id    = d["id"]
        interaction_token = d["token"]

        channel_id = int(d["channel_id"])
        guild_id   = int(d["guild_id"]) if d.get("guild_id") else None

        user_data = d.get("member") or d.get("user")

        guild   = guild_id and Bloxlink.get_guild(guild_id)
        user    = None
        channel = None

        if guild:
            user = Member(state=guild._state, data=user_data, guild=guild)
            channel = find(lambda c: c.id == channel_id, guild.text_channels)
        else:
            user = User(state=Bloxlink._connection, data=user_data)
            channel = DMChannel(me=Bloxlink.user, state=Bloxlink._connection, data={"id": channel_id, "recipients": [user_data]})

        try:
            await handle_slash_command(command_name, guild=guild, channel=channel,
                                        user=user, interaction_id=interaction_id,
                                        interaction_token=interaction_token,
                                        command_id=command_id, subcommand=subcommand,
                                        arguments=command_args)
        except CancelCommand:
            pass
