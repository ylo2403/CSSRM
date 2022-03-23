from resources.structures.Bloxlink import Bloxlink # pylint: disable=import-error, no-name-in-module

@Bloxlink.command
class BindCommand(Bloxlink.Module):
    """bind a discord role to a roblox group, asset, or badge"""

    def __init__(self):
        self.aliases = ["newbind"]
        self.permissions = Bloxlink.Permissions().build("BLOXLINK_MANAGER")
        self.category = "Binds"
        self.slash_enabled = True


    async def __main__(self, CommandArgs):
        await CommandArgs.response.send("change this from the dashboard")
