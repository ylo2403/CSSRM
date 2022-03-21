from resources.structures.Bloxlink import Bloxlink  # pylint: disable=import-error, no-name-in-module
from resources.exceptions import Error, Message, UserNotVerified, BloxlinkBypass, Blacklisted  # pylint: disable=import-error, no-name-in-module
from resources.constants import DEFAULTS, GREEN_COLOR, VERIFY_URL, SELF_HOST  # pylint: disable=import-error, no-name-in-module
from discord.errors import Forbidden, NotFound, HTTPException


verify_as, parse_accounts, update_member, get_nickname, verify_member, count_binds = Bloxlink.get_module("roblox", attrs=["verify_as", "parse_accounts", "update_member", "get_nickname", "verify_member", "count_binds"])
post_event = Bloxlink.get_module("utils", attrs=["post_event"])
has_magic_role = Bloxlink.get_module("extras", attrs=["has_magic_role"])
get_user = Bloxlink.get_module("robloxnew.users", attrs=["get_user"], name_override="users")
get_guild_value = Bloxlink.get_module("cache", attrs=["get_guild_value"])

class SwitchUserCommand(Bloxlink.Module):
    """change your linked Roblox account in a server"""

    def __init__(self):
        self.category = "Account"
        self.aliases = ["switch-user"]
        self.slash_enabled = True

    @staticmethod
    async def validate_server(message, content, prompt, guild):
        content = content.lower()

        if content in ("skip", "next"):
            return message.guild

        if not content.isdigit():
            return None, "A server ID must be a number."

        try:
            guild = await Bloxlink.fetch_guild(int(content))
        except Forbidden:
            return None, "I'm not a member of this server."
        except HTTPException:
            return None, "This is an invalid server ID."
        else:
            return guild


    async def __main__(self, CommandArgs):
        author = CommandArgs.author
        response = CommandArgs.response

        if not SELF_HOST:
            author_data = await self.r.db("bloxlink").table("users").get(str(author.id)).run() or {"id": str(author.id)}

            try:
                primary_account, accounts = await get_user(user=author)

                if accounts:
                    parsed_accounts = await parse_accounts(accounts)
                    parsed_accounts_str = ", ".join(parsed_accounts.keys())

                    parsed_args = await CommandArgs.prompt([
                        {
                            "prompt": "This command will allow you to switch into an account you verified as in the past.\n"
                                    f"If you would like to link __a new account__, then please use `/verify add`.\n\n"
                                    "**__WARNING:__** This will remove __all of your roles__ in the server and give you "
                                    "new roles depending on the server configuration.",
                            "footer": "Say **next** to continue.",
                            "type": "choice",
                            "choices": ["next"],
                            "name": "_",
                            "formatting": False
                        },
                        {
                            "prompt": "Are you trying to change your account for _this_ server? If so, simply say `next`.\nIf not, please provide "
                                    "the __Server ID__ of the server to switch as. Please see this article to find the Server ID: "
                                    "[click here](https://support.discordapp.com/hc/en-us/articles/206346498-Where-can-I-find-my-User-Server-Message-ID->).",
                            "name": "guild",
                            "validation": self.validate_server,
                        },
                        {
                            "prompt": "We'll switch your account for the server **{guild.name}**.\n"
                                    "Please select an account to switch into:```" + parsed_accounts_str + "```",
                            "name": "account",
                            "type": "choice",
                            "choices": list(parsed_accounts.keys())
                        },
                        {
                            "prompt": "Would you like to make this your __primary__ account? Please say **yes** or **no**.",
                            "name": "primary",
                            "type": "choice",
                            "choices": ("yes", "no")
                        }
                    ], last=True)

                    guild = parsed_args["guild"]
                    username = parsed_args["account"]
                    roblox_id = (parsed_accounts.get(username)).id

                    allow_reverify = await get_guild_value(guild, ["allowReVerify", DEFAULTS.get("allowReVerify")])
                    roblox_accounts = author_data.get("robloxAccounts", {})

                    if guild and not allow_reverify:
                        guild_accounts = roblox_accounts.get("guilds", {})
                        chosen_account = guild_accounts.get(str(guild.id))

                        if chosen_account and chosen_account != roblox_id:
                            raise Error("You already selected your account for this server. `allowReVerify` must be "
                                        "enabled for you to change it.")

                    try:
                        member = await guild.fetch_member(author.id)
                    except (Forbidden, NotFound):
                        await verify_member(author, roblox_id, guild=guild, allow_reverify=allow_reverify, primary_account=parsed_args["primary"] == "yes")
                        raise Message("You're not a member of the provided server, so I was only able to update your account internally.", type="success")

                    try:
                        username = await verify_as(
                            member,
                            guild,
                            response     = response,
                            primary      = parsed_args["primary"] == "yes",
                            roblox_id    = roblox_id,
                            update_user  = False)

                    except Message as e:
                        if e.type == "error":
                            await response.error(e)
                        else:
                            await response.send(e)
                    except Error as e:
                        await response.error(e)
                    else:
                        if count_binds(guild) and not await has_magic_role(member, guild, "Bloxlink Bypass"):
                            for role in list(member.roles):
                                if role != guild.default_role and role.name != "Muted":
                                    try:
                                        await member.remove_roles(role, reason="Switched User")
                                    except Forbidden:
                                        pass
                        try:
                            added, removed, nickname, errors, warnings, roblox_user = await update_member(
                                member,
                                guild        = guild,
                                roles        = True,
                                nickname     = True,
                                response     = response,
                                cache        = False)

                        except BloxlinkBypass:
                            await response.info("Since you have the `Bloxlink Bypass` role, I was unable to update your roles/nickname; however, your account was still changed.")

                            return

                        except Blacklisted as b:
                            if isinstance(b.message, str):
                                raise Error(f"{author.mention} has an active restriction for: `{b}`.")
                            else:
                                raise Error(f"{author.mention} has an active restriction from Bloxlink.")
                        else:
                            welcome_message = await get_guild_value(guild, ["welcomeMessage", DEFAULTS.get("welcomeMessage")])
                            welcome_message = await get_nickname(author, welcome_message, roblox_user=roblox_user, is_nickname=False)

                            await post_event(guild, "verification", f"{author.mention} ({author.id}) has **switched their user** to `{username}`.", GREEN_COLOR)

                            await CommandArgs.response.send(welcome_message)

                else:
                    raise Message(f"You only have one account linked! Please use `/verify add` to add another.", type="info")


            except UserNotVerified:
                raise Error(f"You're not linked to Bloxlink. Please use `/verify add`.")

        else:
            raise Message(f"{author.mention}, to verify with Bloxlink, please visit our website at " \
                          f"<{VERIFY_URL}>. It won't take long!\nStuck? See this video: <https://www.youtube.com/watch?v=0SH3n8rY9Fg&list=PLz7SOP-guESE1V6ywCCLc1IQWiLURSvBE&index=2>")
