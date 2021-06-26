from ..structures.Bloxlink import Bloxlink # pylint: disable=import-error, no-name-in-module
from ..exceptions import CancelCommand # pylint: disable=import-error, no-name-in-module



handle_slash_command = Bloxlink.get_module("commands", attrs="handle_slash_command")

@Bloxlink.event
async def on_interaction(interaction):
    data = interaction.data
    command_name = interaction.data.get("name")
    command_id   = interaction.data.get("id")
    command_args = []

    if not command_name:
        return

    subcommand = None

    if data.get("options"):
        for arg in data["options"]:
            if arg.get("value") is not None:
                command_args.append([arg["name"], arg["value"]])
            else:
                subcommand = arg["name"]

    first_response = interaction.response
    followups      = interaction.followup

    guild   = interaction.guild
    channel = interaction.channel
    user    = interaction.user

    if not guild:
        return

    try:
        await handle_slash_command(command_name, guild=guild, channel=channel,
                                    user=user, first_response=first_response,
                                    interaction=interaction,
                                    followups=followups, command_id=command_id,
                                    subcommand=subcommand, arguments=command_args)
    except CancelCommand:
        pass
