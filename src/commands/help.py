from resources.structures.Bloxlink import Bloxlink # pylint: disable=import-error, no-name-in-modules
from resources.exceptions import CancelCommand
from discord import File
from io import BytesIO

fetch = Bloxlink.get_module("utils", attrs=["fetch"])
parse_message = Bloxlink.get_module("commands", attrs="parse_message")

@Bloxlink.command
class HelpCommand(Bloxlink.Module):
    """view information about Bloxlink"""

    def __init__(self):
        self.dm_allowed    = True
        self.slash_enabled = True
        self.arguments = [
            {
                "prompt": "Please specify the command name",
                "optional": True,
                "name": "command_name"
            }
        ]

        self.images = None
        self.urls = [
            "https://i.imgur.com/zQwITet.png",
            "https://i.imgur.com/yv6jfNC.png",
            "https://i.imgur.com/pwMB8wZ.png"
        ]

    async def __setup__(self):
        self.images = []

        for url in self.urls:
            image_data, image_response = await fetch(url=url, bytes=True, raise_on_failure=False)

            if image_response.status == 200:
                self.images.append(image_data)

    async def __main__(self, CommandArgs):
        response = CommandArgs.response
        channel  = CommandArgs.channel
        guild    = CommandArgs.guild

        command_name = CommandArgs.parsed_args["command_name"]

        if command_name:
            await response.command.redirect(CommandArgs, "commands", arguments={"command_name": command_name})

            raise CancelCommand

        if guild and not channel.permissions_for(guild.me).attach_files:
            urls = "\n".join(self.urls)
            await response.send(f"Some general info is below! To view all commands, say `/commands`.\n{urls}")
        else:
            await response.send("Some general info is below! To view all commands, say `/commands`.", files=[File(BytesIO(b), filename=f"image_{i}.png") for i, b in enumerate(self.images)])
