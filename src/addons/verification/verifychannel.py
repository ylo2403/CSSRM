from resources.structures.Bloxlink import Bloxlink # pylint: disable=import-error, no-name-in-module
from resources.constants import DEFAULTS # pylint: disable=import-error, no-name-in-module

import discord

set_guild_value, get_guild_value = Bloxlink.get_module("cache", attrs=["set_guild_value", "get_guild_value"])
VerificationView = Bloxlink.get_module("robloxnew.verifym", attrs=["VerificationView"], name_override="verifym")
has_premium = Bloxlink.get_module("premium", attrs=["has_premium"])


class VerifyChannelModal(discord.ui.Modal, title="Verification Channel"):
    bloxlink_post = discord.ui.TextInput(label="What would you like Bloxlink to write?",
                                                default=DEFAULTS.get("verifyChannelTextModal"),
                                                style=discord.TextStyle.paragraph,
                                                max_length=2000)

    def __init__(self, verify_channel, *args, **kwargs):
        self.verify_channel = verify_channel
        super().__init__(*args, **kwargs)

    async def on_submit(self, interaction: discord.Interaction):
        guild = interaction.guild

        verify_button_text = None

        for child in self.children:
            if child.custom_id == "verify_channel_modal:verify_button_label":
                verify_button_text = child.value

        try:
            await self.verify_channel.send(str(self.bloxlink_post).replace("{server-name}", guild.name), view=VerificationView(verify_button_text or "Verify with Bloxlink", self.bloxlink_post.value))
        except discord.errors.Forbidden:
            await interaction.response.send_message("I was unable to post in your verification channel. Please make sure I have the correct permissions.")
        else:
            await interaction.response.send_message(f"Your new verification channel has been created! {self.verify_channel.mention}")


class VerifyChannelCommand(Bloxlink.Module):
    """create a special verification channel"""

    def __init__(self):
        self.permissions = Bloxlink.Permissions().build("BLOXLINK_MANAGER")
        self.aliases = ["verificationchannel", "verification-channel"]
        self.category = "Administration"
        self.slash_enabled = True
        self.arguments = [
            {
                "prompt": "Do you have an existing verification channel?",
                "type": "channel",
                "name": "existing_channel",
                "optional": True
            }
        ]

    async def __main__(self, CommandArgs):
        response = CommandArgs.response
        guild    = CommandArgs.guild

        is_premium = "premium" in (await has_premium(guild=guild)).features

        existing_channel = CommandArgs.parsed_args["existing_channel"]

        verify_category = discord.utils.find(lambda c: c.name == "Verification", guild.categories) or await guild.create_category(name="Verification")
        verify_channel  = existing_channel or discord.utils.find(lambda c: c.name == "verify", guild.text_channels) or await guild.create_text_channel(name="verify", category=verify_category)

        await verify_channel.set_permissions(guild.me, send_messages=True, read_messages=True)

        verify_instructions = discord.utils.find(lambda c: c.name == "verify-instructions", guild.text_channels)

        try:
            verify_instructions = existing_channel or verify_instructions or verify_channel
            welcome_message = await get_guild_value(guild, "welcomeMessage")

            modal = VerifyChannelModal(verify_channel)

            if is_premium:
                modal.add_item(item=discord.ui.TextInput(label="What text do you want for your Verify button?",
                                default="Verify with Bloxlink",
                                style=discord.TextStyle.paragraph,
                                required=False,
                                max_length=80,
                                custom_id="verify_channel_modal:verify_button_label"))

            modal.add_item(item=discord.ui.TextInput(label="Message after someone verifies",
                            default=welcome_message or DEFAULTS.get("welcomeMessage"),
                            style=discord.TextStyle.paragraph,
                            required=False,
                            max_length=2000,
                            custom_id="verify_channel_modal:welcome_message"))

            await verify_instructions.set_permissions(guild.me, send_messages=True, read_messages=True)
            await verify_instructions.set_permissions(guild.default_role, send_messages=False, read_messages=True)

            await response.send_modal(modal)

            await modal.wait()

            success_text = f"All done! Your new verification channel is {verify_channel.mention}!"

            if not is_premium:
                success_text += ("\n\n**Pro-tip:** Bloxlink Premium subscribers can "
                                "[customize the text of the verification button and customize the text that Bloxlink posts!](<https://twitter.com/bloxlink/status/1521487474949857282>)\n"
                                f"Subscribe from our [Dashboard!](<https://blox.link/dashboard/guilds/{guild.id}/premium>)")

            await response.send(success_text)



        except discord.errors.Forbidden:
            await response.send("I encountered a permission error. Please make sure I can create channels and set permissions.")
