from resources.structures.Bloxlink import Bloxlink # pylint: disable=import-error, no-name-in-module
from resources.exceptions import RobloxNotFound, Error, RobloxAPIError, Message # pylint: disable=import-error, no-name-in-module
from resources.constants import LIMITS # pylint: disable=import-error, no-name-in-module
from discord import Embed, Object
import re


get_group, get_user = Bloxlink.get_module("roblox", attrs=["get_group", "get_user"])
set_guild_value = Bloxlink.get_module("cache", attrs=["set_guild_value"])
get_features = Bloxlink.get_module("premium", attrs=["get_features"])


RESTRICTION_NAME_DB_USER_MAP = {
    "groups": "Groups",
    "users": "Users",
    "robloxAccounts": "Roblox Accounts",
    "roles": "Roles"
}

RESTRICTION_NAME_COMMAND_DB_MAP = {
    "user": "users",
    "group_url": "groups",
    "discord_user": "users",
    "roblox_username": "robloxAccounts",
    "discord_role": "roles"
}

@Bloxlink.command
class RestrictCommand(Bloxlink.Module):
    """restrict a Roblox user or group from verifying in your server"""

    def __init__(self):
        self.permissions = Bloxlink.Permissions().build("BLOXLINK_MANAGER")
        self.category = "Administration"
        self.aliases = ["restriction"]
        self.slash_enabled = True
        self.slash_only = True
        self._remove_data_regex = re.compile("(.*)-(.*)")

    async def auto_complete_group(self, interaction, command_args, focused_option):
        if not focused_option:
            return

        try:
            group = await get_group(focused_option, full_group=True)
        except (RobloxNotFound, RobloxAPIError):
            return []

        return [
            [f"{group.name} ({group.group_id})", group.group_id]
        ]

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


    async def auto_complete_restrictions(self, interaction, command_args, focused_option):
        focused_option = focused_option.lower()

        guild = interaction.guild
        guild_data = await self.r.table("guilds").get(str(guild.id)).run() or {}
        restrictions = guild_data.get("restrictions") or {}
        parsed_restrictions = []

        for restriction_name, title_name in RESTRICTION_NAME_DB_USER_MAP.items():
            if restrictions.get(restriction_name):
                for restriction_id, restriction_data in restrictions[restriction_name].items():
                    restriction_data["title"] = title_name[:-1] # remove ending "s"
                    restriction_data["internal_name"] = restriction_name
                    restriction_data["id"] = restriction_id

                    parsed_restrictions.append(restriction_data)


        if focused_option:
            return [
                [f"{restriction['title']}: {restriction['name']}", f"{restriction['internal_name']}-{restriction['id']}"] for restriction in parsed_restrictions if restriction["name"].lower().startswith(focused_option)
            ][:25]
        else:
            return [
                [f"{restriction['title']}: {restriction['name']}", f"{restriction['internal_name']}-{restriction['id']}"] for restriction in parsed_restrictions
            ][:25]


    async def __main__(self, CommandArgs):
        pass

    @Bloxlink.subcommand(arguments=[
        {
            "prompt": "Restrict a Roblox user from verifying in your server.",
            "name": "roblox_username",
            "type": "string",
            "auto_complete": auto_complete_roblox_user,
            "optional": True
        },
        {
            "prompt": "Restrict members from a Roblox group from verifying in your server.",
            "name": "group_url",
            "type": "string",
            "auto_complete": auto_complete_group,
            "optional": True
        },
        {
            "prompt": "Restrict a Discord user from verifying in your server.",
            "name": "discord_user",
            "type": "user",
            "optional": True
        },
        {
            "prompt": "Restrict people with a Discord role from verifying.",
            "name": "discord_role",
            "type": "role",
            "optional": True
        },
        {
            "prompt": "Why are you restricting this user? This note will be available to you later.",
            "name": "reason",
            "type": "string",
            "optional": True
        },
    ])
    async def add(self, CommandArgs):
        """restrict certain people or groups from verifying in your server"""

        guild_data   = CommandArgs.guild_data
        parsed_args  = CommandArgs.parsed_args
        response     = CommandArgs.response
        author       = CommandArgs.author
        guild        = CommandArgs.guild
        prefix       = CommandArgs.prefix

        reason       = parsed_args["reason"]

        got_entry = False

        restrictions = guild_data.get("restrictions", {})
        len_restrictions = len(restrictions.get("users", [])) + len(restrictions.get("robloxAccounts", [])) + len(restrictions.get("groups", []))

        if len_restrictions >= LIMITS["RESTRICTIONS"]["FREE"]:
            profile, _ = await get_features(Object(id=guild.owner_id), guild=guild)

            if not profile.features.get("premium"):
                raise Error(f"You have the max restrictions `({LIMITS['RESTRICTIONS']['FREE']})` allowed for free servers! You may "
                            f"unlock **additional restrictions** `({LIMITS['RESTRICTIONS']['PREMIUM']})` by subscribing to premium. Find out "
                            f"more info with `{prefix}donate`.\nFor now, you may remove restrictions with `{prefix}restrict remove` "
                            "to add additional restrictions.")
            else:
                if len_restrictions >= LIMITS["RESTRICTIONS"]["PREMIUM"]:
                    raise Error("You have the max restrictions for this server! Please delete some before adding more.")


        for command_arg, value in parsed_args.items():
            if value and command_arg in RESTRICTION_NAME_COMMAND_DB_MAP:
                display_name = None
                idx = None
                command_arg_db_name = RESTRICTION_NAME_COMMAND_DB_MAP[command_arg]

                try:
                    if command_arg == "group_url":
                        group = await get_group(value)
                        display_name = group.name
                        idx = group.group_id
                        got_entry = True
                    elif command_arg == "discord_user":
                        display_name = str(value)
                        idx = value.id
                        got_entry = True
                    elif command_arg == "roblox_username":
                        roblox_user, _ = await get_user(roblox_id=value)
                        display_name = roblox_user.username
                        idx = roblox_user.id
                        got_entry = True
                    elif command_arg == "discord_role":
                        display_name = str(value)
                        idx = value.id
                        got_entry = True

                except RobloxNotFound:
                    raise Error(f"This `{command_arg_db_name}` could not be found!")

                restrictions[command_arg_db_name] = restrictions.get(command_arg_db_name, {})
                restrictions[command_arg_db_name][str(idx)] = {"name": display_name, "addedBy": str(author.id), "reason": reason}

        if not got_entry:
            raise Message("You need to supply at least one argument!", type="silly")


        guild_data["restrictions"] = restrictions
        await set_guild_value(guild, "restrictions", restrictions)

        await self.r.table("guilds").insert(guild_data, conflict="update").run()

        await response.success(f"Successfully **updated** your restrictions!")

    @Bloxlink.subcommand()
    async def view(self, CommandArgs):
        """view your restricted users or groups"""

        response = CommandArgs.response
        guild    = CommandArgs.guild

        guild_data = CommandArgs.guild_data
        restrictions = guild_data.get("restrictions", {})

        if not restrictions:
            return await response.silly("You have no restrictions!")

        embed = Embed(title=f"Server Restrictions for {guild.name}", description="These members will not be able to verify in your server!")

        for restriction_type, restriction_data in restrictions.items():
            if restriction_data:
                embed.add_field(name=RESTRICTION_NAME_DB_USER_MAP[restriction_type], value="\n".join(["**" + y['name'] + '** (' + x + ')' + ' | Reason: ' + str(y['reason']) + ' | Added by: ' + (f'<@{y["addedBy"]}>' if y['addedBy'] else y['addedBy']) for x,y in restriction_data.items()]))

        await response.send(embed=embed)


    @Bloxlink.subcommand(arguments=[
        {
            "prompt": "Please choose your restriction to remove, or search for one.",
            "name": "restriction_data",
            "auto_complete": auto_complete_restrictions
        }
    ])
    async def remove(self, CommandArgs):
        """allow a user or group back in your server"""

        guild    = CommandArgs.guild
        response = CommandArgs.response

        guild_data = CommandArgs.guild_data
        restrictions = guild_data.get("restrictions") or {}

        remove_data = CommandArgs.parsed_args["restriction_data"]
        remove_data_match = self._remove_data_regex.search(remove_data)

        if not remove_data_match:
            raise Message("You must select an option from the dropdown!", type="silly")
        else:
            directory_name, remove_id = remove_data_match.group(0), remove_data_match.group(1)

        if directory_name and remove_id:
            if restrictions.get(directory_name, {}).get(remove_id):
                restrictions[directory_name].pop(remove_id)

                if not restrictions[directory_name]:
                    restrictions.pop(directory_name, None)

                guild_data["restrictions"] = restrictions
                await set_guild_value(guild, "restrictions", restrictions)

                await self.r.table("guilds").insert(guild_data, conflict="replace").run()

                await response.success(f"Successfully **removed** this **{directory_name[:-1]}** from your restrictions.")

            else:
                raise Error(f"This **{directory_name[:-1]}** isn't restricted!")
