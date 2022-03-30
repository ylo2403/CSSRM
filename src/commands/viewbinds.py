from resources.structures.Bloxlink import Bloxlink # pylint: disable=import-error, no-name-in-module
from discord import Embed
from resources.exceptions import Message, RobloxNotFound # pylint: disable=import-error, no-name-in-module
from resources.constants import ARROW # pylint: disable=import-error, no-name-in-module

get_binds, get_group, count_binds = Bloxlink.get_module("roblox", attrs=["get_binds", "get_group", "count_binds"])


@Bloxlink.command
class ViewBindsCommand(Bloxlink.Module):
    """view your server bound roles"""

    def __init__(self):
        self.category = "Binds"
        self.aliases = ["binds", "view-binds"]
        self.slash_enabled = True

    async def __main__(self, CommandArgs):
        response = CommandArgs.response

        await response.send("view your binds from the dashboard")
