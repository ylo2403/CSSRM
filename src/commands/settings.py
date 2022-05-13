from resources.structures.Bloxlink import Bloxlink # pylint: disable=import-error, no-name-in-module, no-name-in-module


@Bloxlink.command
class SettingsCommand(Bloxlink.Module):
    """change, view, or reset your Bloxlink settings"""

    def __init__(self):
        self.permissions = Bloxlink.Permissions(manage_guild=True)
        self.category = "Administration"
        self.slash_enabled = True

    async def __main__(self, CommandArgs):
        response = CommandArgs.response

        await CommandArgs.response.send("You can modify your settings from our dashboard: https://blox.link/dashboard")
