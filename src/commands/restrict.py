from resources.structures.Bloxlink import Bloxlink # pylint: disable=import-error
from resources.exceptions import RobloxNotFound, Error, UserNotVerified, RobloxAPIError # pylint: disable=import-error
from resources.constants import LIMITS # pylint: disable=import-error
from discord import Embed
import re


get_group, get_user, parse_accounts = Bloxlink.get_module("roblox", attrs=["get_group", "get_user", "parse_accounts"])
user_resolver = Bloxlink.get_module("resolver", attrs="user_resolver")
set_guild_value = Bloxlink.get_module("cache", attrs=["set_guild_value"])


@Bloxlink.command
class RestrictCommand(Bloxlink.Module):
    """restrict a Roblox user or group from verifying in your server"""

    def __init__(self):
        self.permissions = Bloxlink.Permissions().build("BLOXLINK_MANAGER")
        self.category = "Administration"

        self._roblox_group_regex = re.compile(r"roblox.com/groups/(\d+)/")

    async def resolve_restriction(self, message, content, prompt):
        # user check
        user, _ = await user_resolver({}, message, message.guild, content)

        if user:
            return ("users", "Discord user", user, user.id, str(user))

        if content.isdigit():
            # if there's a group and roblox account with the same ID
            try:
                group = await get_group(content, full_group=True)
            except (RobloxNotFound, RobloxAPIError):
                pass
            else:
                try:
                    account, _ = await get_user(roblox_id=content)
                except (RobloxNotFound, RobloxAPIError):
                    pass
                else:
                    restrict_what = (await prompt([
                        {
                            "prompt": "There's some ambiguity! There's both a Roblox account and Group with this ID.\n\n"
                                      "Are you trying to restrict a **group** or a **roblox account**?",
                            "name": "restrict_what",
                            "type": "choice",
                            "choices": ("group", "roblox account")
                        }
                    ]))["restrict_what"]

                    if restrict_what == "group":
                        return ("groups", "Group", group, group.group_id, group.name)
                    else:
                        return ("robloxAccounts", "Roblox account", account, account.id, account.username)

        # group check
        regex_search_group = self._roblox_group_regex.search(content)

        if regex_search_group:
            group_id = regex_search_group.group(1)
        else:
            group_id = content

        try:
            group = await get_group(group_id, full_group=True)
        except (RobloxNotFound, RobloxAPIError):
            pass
        else:
            return ("groups", "Group", group, group.group_id, group.name)

        # roblox username/id check
        username = roblox_id = None

        if content.isdigit():
            roblox_id = content
        else:
            username = content
        try:
            account, _ = await get_user(username=username, roblox_id=roblox_id)
        except (RobloxNotFound, RobloxAPIError):
            pass
        else:
            return ("robloxAccounts", "Roblox account", account, account.id, account.username)

        return None, "No results were found! Please either provide a Group URL/ID, a Discord user, or a Roblox username/id."

    async def __main__(self, CommandArgs):
        guild_data = CommandArgs.guild_data
        response   = CommandArgs.response
        author     = CommandArgs.author
        guild      = CommandArgs.guild

        restrictions = guild_data.get("restrictions", {})
        len_restrictions = len(restrictions.get("users", [])) + len(restrictions.get("robloxAccounts", [])) + len(restrictions.get("groups", []))

        if len_restrictions >= LIMITS["RESTRICTIONS"]:
            raise Error("You have the max restrictions for this server! Please delete some before adding more.")

        parsed_args = await CommandArgs.prompt([
            {
                "prompt": "Please either mention a user, give a Group URL, or a Roblox username.",
                "name": "resolvable",
                "validation": self.resolve_restriction
            },
            {
                "prompt": "What's the reason for this restriction? __This will be publicly displayed to "
                          "people who try to verify and are restricted.__\n\nOptionally, say `skip` to set "
                          "a default text.",
                "name": "reason",
                "exceptions": ("skip",)
            }
        ])

        resolvable = parsed_args["resolvable"]
        reason     = parsed_args["reason"] if parsed_args["reason"] != "skip" else None

        restrictions[resolvable[0]] = restrictions.get(resolvable[0], {})
        restrictions[resolvable[0]][str(resolvable[3])] = {"name": resolvable[4], "addedBy": str(author.id), "reason": reason}

        if resolvable[0] == "users":
            # poison ban
            try:
                _, accounts = await get_user("username", author=author, everything=False, basic_details=True)
            except UserNotVerified:
                pass
            else:
                restrictions["robloxAccounts"] = restrictions.get("robloxAccounts", {})
                parsed_accounts = await parse_accounts(accounts) # TODO: poison ban their discord accounts as well?

                for roblox_account in parsed_accounts.values():
                    restrictions["robloxAccounts"][roblox_account.id] = {"name": roblox_account.username, "addedBy": str(author.id), "reason": reason}

        guild_data["restrictions"] = restrictions
        await set_guild_value(guild, "restrictions", restrictions)

        await self.r.table("guilds").insert(guild_data, conflict="update").run()

        await response.success(f"Successfully **added** {resolvable[1]} **{resolvable[4]}** to your restrictions.")


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
                embed.add_field(name=restriction_type.title(), value=", ".join([y['name'] + ' (' + x + ')' for x,y in restriction_data.items()]))

        await response.send(embed=embed)


    @Bloxlink.subcommand()
    async def remove(self, CommandArgs):
        """allow a user or group back in your server"""

        guild    = CommandArgs.guild
        response = CommandArgs.response

        guild_data = CommandArgs.guild_data
        restrictions = guild_data.get("restrictions", {})

        resolvable = (await CommandArgs.prompt([{
            "prompt": "Please either mention a user, give a Group URL, or a Roblox username.",
            "name": "resolvable",
            "validation": self.resolve_restriction
        }]))["resolvable"]

        if restrictions.get(resolvable[0], {}).get(str(resolvable[3])):
            restrictions[resolvable[0]].pop(str(resolvable[3]))

            if not restrictions[resolvable[0]]:
                restrictions.pop(resolvable[0], None)

            guild_data["restrictions"] = restrictions
            await set_guild_value(guild, "restrictions", restrictions)

            await self.r.table("guilds").insert(guild_data, conflict="replace").run()

            await response.success(f"Successfully **removed** this **{resolvable[1]}** from your restrictions.")

        else:
            raise Error(f"This **{resolvable[1]}** isn't restricted!")
