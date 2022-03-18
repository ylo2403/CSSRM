from resources.structures.Bloxlink import Bloxlink # pylint: disable=import-error, no-name-in-module, no-name-in-module


@Bloxlink.command
class SettingsCommand(Bloxlink.Module):
    """change, view, or reset your Bloxlink settings"""

    def __init__(self):
        self.permissions = Bloxlink.Permissions().build("BLOXLINK_MANAGER")
        self.category = "Administration"

    async def __main__(self, CommandArgs):
        response = CommandArgs.response

        await response.send("You can change your server settings from our website: {link}")
