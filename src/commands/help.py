from resources.structures.Bloxlink import Bloxlink # pylint: disable=import-error



@Bloxlink.command
class HelpCommand(Bloxlink.Module):
    """view information about Bloxlink"""

    def __init__(self):
        self.dm_allowed    = True
        self.slash_enabled = True

    async def __main__(self, CommandArgs):
        response = CommandArgs.response
        prefix   = CommandArgs.prefix

        await response.send(f"Some general info is below! To view all commands, say `{prefix}commands`.\n"
        "https://i.imgur.com/zQwITet.png\nhttps://i.imgur.com/yv6jfNC.png\nhttps://i.imgur.com/pwMB8wZ.png")
