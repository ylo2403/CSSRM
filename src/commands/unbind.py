from resources.structures.Bloxlink import Bloxlink # pylint: disable=import-error, no-name-in-module


@Bloxlink.command
class UnBindCommand(Bloxlink.Module):
    """delete a role bind from your server"""

    def __init__(self):
        self.permissions = Bloxlink.Permissions().build("BLOXLINK_MANAGER")
        self.category = "Binds"
        self.aliases = ["delbind", "delbinds", "un-bind", "del-bind"]
        self.slash_enabled = True

    async def __main__(self, CommandArgs):
        await CommandArgs.response("test")
