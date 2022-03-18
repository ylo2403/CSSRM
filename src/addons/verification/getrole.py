from resources.structures import Bloxlink, Card # pylint: disable=import-error, no-name-in-module, no-name-in-module
from resources.exceptions import Message, UserNotVerified, Error, BloxlinkBypass, Blacklisted, PermissionError # pylint: disable=import-error, no-name-in-module, no-name-in-module
from resources.constants import GREEN_COLOR, VERIFY_URL # pylint: disable=import-error, no-name-in-module, no-name-in-module
import discord

format_update_embed, guild_obligations = Bloxlink.get_module("roblox", attrs=["format_update_embed", "guild_obligations"])
post_event = Bloxlink.get_module("utils", attrs=["post_event"])
get_accounts = Bloxlink.get_module("robloxnew.users", attrs=["get_accounts"], name_override="users")



class GetRoleCommand(Bloxlink.Module):
    """get your server roles"""

    def __init__(self):
        self.category = "Account"
        self.cooldown = 5
        self.aliases = ["getroles", "get-roles", "get-role"]
        self.slash_enabled = True
        self.slash_defer = True

    @Bloxlink.flags
    async def __main__(self, CommandArgs):
        guild = CommandArgs.guild
        author = CommandArgs.author
        response = CommandArgs.response

        try:
            old_nickname = author.display_name

            added, removed, nickname, errors, warnings, roblox_user = await guild_obligations(
                author,
                guild                = guild,
                join                 = True,
                roles                = True,
                nickname             = True,
                cache                = False,
                response             = response,
                dm                   = False,
                exceptions           = ("BloxlinkBypass", "Blacklisted", "UserNotVerified", "PermissionError", "RobloxDown", "RobloxAPIError")
            )

        except BloxlinkBypass:
            raise Message("Since you have the `Bloxlink Bypass` role, I was unable to update your roles/nickname.", type="info")

        except Blacklisted as b:
            if isinstance(b.message, str):
                raise Error(f"{author.mention} has an active restriction for: `{b}`")
            else:
                raise Error(f"{author.mention} has an active restriction from Bloxlink.")

        except UserNotVerified:
            view = discord.ui.View()
            view.add_item(item=discord.ui.Button(style=discord.ButtonStyle.link, label="Verify with Bloxlink", url=VERIFY_URL, emoji="🔗"))
            view.add_item(item=discord.ui.Button(style=discord.ButtonStyle.link, label="Stuck? See a Tutorial", emoji="❔",
                                                 url="https://www.youtube.com/watch?v=0SH3n8rY9Fg&list=PLz7SOP-guESE1V6ywCCLc1IQWiLURSvBE&index=2"))

            await response.send("To verify with Bloxlink, click the link below.", mention_author=True, view=view)

        except PermissionError as e:
            raise Error(e.message)

        else:
            welcome_message, card, embed = await format_update_embed(
                roblox_user,
                author,
                guild=guild,
                added=added, removed=removed, errors=errors, warnings=warnings, nickname=nickname if old_nickname != nickname else None,
                guild_data=guild_data
            )

            message = await response.send(welcome_message, files=[card.front_card_file] if card else None, view=card.view if card else None, embed=embed, mention_author=True)

            if card:
                card.response = response
                card.message = message
                card.view.message = message

            await post_event(guild, "verification", f"{author.mention} ({author.id}) has **verified** as `{roblox_user.username}`.", GREEN_COLOR)
