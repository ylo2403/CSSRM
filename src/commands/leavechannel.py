from resources.structures.Bloxlink import Bloxlink # pylint: disable=import-error, no-name-in-module, no-name-in-module
from resources.constants import SERVER_VERIFIED_TEMPLATES, UNVERIFIED_TEMPLATES, BROWN_COLOR # pylint: disable=import-error, no-name-in-module, no-name-in-module
from resources.exceptions import Message # pylint: disable=import-error, no-name-in-module, no-name-in-module


post_event = Bloxlink.get_module("utils", attrs=["post_event"])
set_guild_value = Bloxlink.get_module("cache", attrs=["set_guild_value"])


@Bloxlink.command
class LeaveChannelCommand(Bloxlink.Module):
    """posts about people who leave the server in your channel."""

    def __init__(self):
        self.permissions = Bloxlink.Permissions().build("BLOXLINK_MANAGER")
        self.category = "Administration"
        self.arguments = [{
            "prompt": "Would you like to alter/disable the leave messages for **verified** or **unverified** users?",
            "type": "choice",
            "choices": ("verified", "unverified"),
            "name": "subcommand"
        }]
        self.hidden = True
        self.aliases = ["leave-channel"]

    async def __main__(self, CommandArgs):
        subcommand = CommandArgs.parsed_args["subcommand"]
        if subcommand == "verified":
            await self.verified(CommandArgs)
        elif subcommand == "unverified":
            await self.unverified(CommandArgs)

    @Bloxlink.subcommand()
    async def verified(self, CommandArgs):
        """set the leave message of people who are VERIFIED on Bloxlink"""

        guild_data = CommandArgs.guild_data
        leave_channel = guild_data.get("leaveChannel") or {}
        verified_message = leave_channel.get("verified")

        author = CommandArgs.author
        guild = CommandArgs.guild

        response = CommandArgs.response

        if verified_message:
            response.delete(await response.send("When people leave your server and are **VERIFIED** on Bloxlink, this message "
                                                "will be posted:"))
            response.delete(await response.send(f"```{verified_message['message']}```"))

        parsed_args_1 = (await CommandArgs.prompt([{
            "prompt": "Would you like to **change** the message people get when they leave and are verified, or "
                        "would you like to **disable** this feature?\n\nPlease specify: (change, disable)",
            "name": "option",
            "type": "choice",
            "choices": ("change", "disable")
        }]))["option"]

        if parsed_args_1 == "change":
            parsed_args_2 = await CommandArgs.prompt([
                {
                    "prompt": "What would you like the text of the Verified Leave Message to be? You may use "
                             f"these templates: ```{SERVER_VERIFIED_TEMPLATES}```",
                    "name": "text",
                    "max": 1500,
                    "formatting": False
                },
                {
                    "prompt": "Which **channel** would you like the leave messages to be posted in?",
                    "name": "channel",
                    "type": "channel"
                },
                {
                    "prompt": "Would you like users' Roblox avatars to be included in the messages? Turning this on "
                              "will make all posted messages in an embed format; otherwise, just text will be used.\n\n"
                              "Please either say **yes** or **no**.",
                    "name": "include_avatar",
                    "type": "choice",
                    "choices": ("yes", "no")
                }
            ], last=True)

            channel = parsed_args_2["channel"]
            text    = parsed_args_2["text"]
            include_avatar = parsed_args_2["include_avatar"] == "yes"
            includes = {}

            if include_avatar:
                includes["avatar"] = True

                parsed_args_3 = await CommandArgs.prompt([
                    {
                        "prompt": "Would you like this embed to ping people?\n\n"
                                  "Please either say **yes** or **no**.",
                        "name": "ping",
                        "type": "choice",
                        "choices": ("yes", "no")
                    },
                    {
                        "prompt": "Would you like to include additional metadata in the embed, "
                                  "such as the user's Roblox age?\n\n"
                                  "Please either say **yes** or **no**.",
                        "name": "additional_metadata",
                        "type": "choice",
                        "choices": ("yes", "no")
                    },
                ], last=True)

                if parsed_args_3["ping"] == "yes":
                    includes["ping"] = True

                if parsed_args_3["additional_metadata"] == "yes":
                    includes["metadata"] = True

            leave_channel["verified"] = {"channel": str(channel.id), "message": text, "includes": includes}
            guild_data["leaveChannel"] = leave_channel

            await set_guild_value(guild, "leaveChannel", leave_channel)

            await self.r.table("guilds").insert(guild_data, conflict="update").run()

        elif parsed_args_1 == "disable":
            leave_channel.pop("verified", None)
            guild_data["leaveChannel"] = leave_channel

            await set_guild_value(guild, "leaveChannel", leave_channel)

            await self.r.table("guilds").insert(guild_data, conflict="replace").run()

        await post_event(guild, guild_data, "configuration", f"{author.mention} ({author.id}) has **disabled** the `leaveChannel` option for `verified` members.", BROWN_COLOR)

        raise Message(f"Successfully **{parsed_args_1}d** your leave message.", type="success")

    @Bloxlink.subcommand()
    async def unverified(self, CommandArgs):
        """set the leave message of people who are UNVERIFIED on Bloxlink"""

        guild_data = CommandArgs.guild_data
        leave_channel = guild_data.get("leaveChannel") or {}
        unverified_message = leave_channel.get("unverified")

        author = CommandArgs.author
        guild = CommandArgs.guild

        response = CommandArgs.response

        if unverified_message:
            response.delete(await response.send("When people leave your server and are **UNVERIFIED** on Bloxlink, this message "
                                                "will be posted:"))
            response.delete(await response.send(f"```{unverified_message['message']}```"))

        parsed_args_1 = (await CommandArgs.prompt([{
            "prompt": "Would you like to **change** the message people get when they leave and are unverified, or "
                        "would you like to **disable** this feature?\n\nPlease specify: (change, disable)",
            "name": "option",
            "type": "choice",
            "choices": ("change", "disable")
        }]))["option"]

        if parsed_args_1 == "change":
            parsed_args_2 = await CommandArgs.prompt([
                {
                    "prompt": "What would you like the text of the Unverified Leave Message to be? You may use "
                             f"these templates: ```{UNVERIFIED_TEMPLATES}```",
                    "name": "text",
                    "max": 1500,
                    "formatting": False
                },
                {
                    "prompt": "Which **channel** would you like the leave messages to be posted in?",
                    "name": "channel",
                    "type": "channel"
                },
                {
                    "prompt": "Would you like to keep the leave messages in an embed format, or keep it as text?\nIt's "
                              "recommended to say `embed` if you chose to include avatars for the `verified` message "
                              "so the verified and unverified leave messages look similar.\n\n"
                              "Please either say **embed** or **text**.",
                    "name": "type",
                    "type": "choice",
                    "choices": ("embed", "text")
                }
            ], last=True)

            channel = parsed_args_2["channel"]
            text    = parsed_args_2["text"]
            embed_format = parsed_args_2["type"] == "embed"
            includes = {}

            if embed_format:
                parsed_args_3 = await CommandArgs.prompt([
                    {
                        "prompt": "Would you like this embed to ping people?\n\n"
                                  "Please either say **yes** or **no**.",
                        "name": "ping",
                        "type": "choice",
                        "choices": ("yes", "no")
                    },
                ], last=True)

                if parsed_args_3["ping"] == "yes":
                    includes["ping"] = True

            leave_channel["unverified"] = {"channel": str(channel.id), "message": text, "includes": includes, "embed": embed_format}
            guild_data["leaveChannel"] = leave_channel

            await set_guild_value(guild, "leaveChannel", leave_channel)

            await self.r.table("guilds").insert(guild_data, conflict="update").run()

        elif parsed_args_1 == "disable":
            leave_channel.pop("unverified", None)
            guild_data["leaveChannel"] = leave_channel

            await set_guild_value(guild, "leaveChannel", leave_channel)

            await self.r.table("guilds").insert(guild_data, conflict="replace").run()

        await post_event(guild, guild_data, "configuration", f"{author.mention} ({author.id}) has **disabled** the `leaveChannel` option for `verified` members.", BROWN_COLOR)

        raise Message(f"Successfully **{parsed_args_1}d** your leave message.", type="success")
