from resources.structures.Bloxlink import Bloxlink # pylint: disable=import-error, no-name-in-module, no-name-in-module
from resources.exceptions import Error, RobloxNotFound, RobloxAPIError, Message, UserNotVerified
from src.resources.exceptions import UserNotVerified # pylint: disable=import-error, no-name-in-module, no-name-in-module

get_user, get_binds = Bloxlink.get_module("roblox", attrs=["get_user", "get_binds"])


@Bloxlink.command
class GetInfoCommand(Bloxlink.Module):
    """retrieve the Roblox information of a user"""

    def __init__(self):
        self.arguments = [
            {
                "prompt": "Please enter a Roblox username or Roblox ID.",
                "name": "roblox_name",
                "auto_complete": self.auto_complete_roblox_user,
                "optional": True
            },
          {
                "prompt": "Please specify a Discord user.",
                "name": "discord_user",
                "type": "user",
                "optional": True
            }
        ]
        self.cooldown = 5
        self.dm_allowed = True
        self.slash_enabled = True
        self.slash_defer = True
        self.slash_only = True
        self.aliases = ["robloxsearch", "rs", "whois"] # FIXME

    async def auto_complete_roblox_user(self, interaction, command_args, focused_option):
        if not focused_option:
            return []

        try:
            if focused_option.isdigit():
                roblox_user, _ = await get_user(roblox_id=focused_option, cache=True)
            else:
                roblox_user, _ = await get_user(username=focused_option, cache=True)

        except (RobloxNotFound, RobloxAPIError):
            return []

        return [[f"{roblox_user.username} ({roblox_user.id})", roblox_user.id]]


    async def __main__(self, CommandArgs):
        response = CommandArgs.response
        guild = CommandArgs.guild

        roblox_id    = CommandArgs.parsed_args["roblox_name"]
        discord_user = CommandArgs.parsed_args["discord_user"]

        if roblox_id and discord_user:
            raise Message("Please only specify a Roblox username OR a Discord user!", type="silly")

        elif not (roblox_id or discord_user):
            discord_user = CommandArgs.author

        if guild:
            role_binds, group_ids, _ = await get_binds(guild_data=CommandArgs.guild_data, trello_board=CommandArgs.trello_board)
        else:
            role_binds, group_ids = {}, {}

        try:
            _, _ = await get_user(author=discord_user, roblox_id=roblox_id, group_ids=(group_ids, role_binds), send_embed=True, guild=guild, response=response, everything=True)
        except RobloxNotFound:
            raise Error("This Roblox account doesn't exist.")
        except RobloxAPIError:
            raise Error("The Roblox API appears to be down so I was unable to retrieve the information. Please try again later.")
        except UserNotVerified:
            raise Error("This user is not linked to Bloxlink!")
