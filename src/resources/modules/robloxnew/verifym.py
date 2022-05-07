from ...structures import Bloxlink, Response # pylint: disable=no-name-in-module, import-error
from ...exceptions import BloxlinkBypass, Blacklisted, PermissionError, UserNotVerified, Message, Error, RobloxAPIError # pylint: disable=import-error, no-name-in-module
from resources.constants import VERIFY_URL, VERIFY_URL_GUILD, DEFAULTS # pylint: disable=import-error, no-name-in-module
import discord

guild_obligations, format_update_embed = Bloxlink.get_module("roblox", attrs=["guild_obligations", "format_update_embed"]) # LEGACY METHODS
has_premium = Bloxlink.get_module("premium", attrs=["has_premium"])


@Bloxlink.module
class VerifyM(Bloxlink.Module):
    def __init__(self):
        self.client.add_view(self.VerificationView())

    class VerificationView(discord.ui.View):
        """adds a verification button that when pressed, verifies the user"""

        def __init__(self, verify_button_text=None, intro_message=None):
            super().__init__(timeout=None)

            if intro_message != DEFAULTS.get("verifyChannelTextModal"):
                self.add_item(item=discord.ui.Button(label="The text above was set by the Server Admins. ONLY verify from https://blox.link.",
                                                     disabled=True,
                                                     custom_id="verify_view:warning_button",
                                                     row=0))

            verify_button = discord.ui.Button(label=verify_button_text,
                                              emoji="<:chain:970894927196209223>",
                                              style=discord.ButtonStyle.green,
                                              custom_id="verify_view:verify_button",
                                              row=1)
            verify_button.callback = self.verify_button_click
            self.add_item(item=verify_button)

            self.add_item(item=discord.ui.Button(style=discord.ButtonStyle.link, label="Need help?", emoji="❔",
                          url="https://www.youtube.com/playlist?list=PLz7SOP-guESE1V6ywCCLc1IQWiLURSvBE", row=1))


        async def verify_button_click(self, interaction: discord.Interaction):
            guild  = interaction.guild
            user   = interaction.user

            old_nickname = user.display_name

            await interaction.response.defer()

            response = Response.from_interaction(interaction)

            try:
                added, removed, nickname, errors, warnings, roblox_user = await guild_obligations(
                    response.args.author,
                    join                 = True,
                    guild                = guild,
                    roles                = True,
                    nickname             = True,
                    cache                = False,
                    response             = response,
                    dm                   = False,
                    exceptions           = ("BloxlinkBypass", "Blacklisted", "UserNotVerified", "PermissionError", "RobloxDown", "RobloxAPIError")
                )

            except BloxlinkBypass:
                await response.send("Since you have the `Bloxlink Bypass` role, I was unable to update your roles/nickname.", type="info")

            except Blacklisted as b:
                if isinstance(b.message, str):
                    await response.send(f"{user.mention} has an active restriction for: `{b}`")
                else:
                    await response.send(f"{user.mention} has an active restriction from Bloxlink.")

            except UserNotVerified:
                verify_link = await VerifyM.get_verify_link(guild)

                await response.send(f"You are not verified with Bloxlink! You can verify by going to [https://blox.link/verify]({verify_link}).", hidden=True)


            except PermissionError as e:
                raise Error(e.message)

            else:
                welcome_message, card, embed = await format_update_embed(
                    roblox_user,
                    user,
                    guild=guild,
                    added=added, removed=removed, errors=errors, warnings=warnings, nickname=nickname if old_nickname != nickname else None,
                )

                message = await response.send(welcome_message, files=[card.front_card_file] if card else None, view=card.view if card else None, embed=embed, hidden=True)

                if card:
                    card.response = response
                    card.message = message
                    card.view.message = message

                    #await post_event(guild, "verification", f"{user.mention} ({user.id}) has **verified** as `{roblox_user.username}`.", GREEN_COLOR)


    @staticmethod
    async def get_verify_link(guild):
        is_premium = "premium" in (await has_premium(guild=guild)).features if guild else False

        return VERIFY_URL_GUILD.format(guild=guild.id) if is_premium else VERIFY_URL


    async def update_user(self, user, guild):
        pass
