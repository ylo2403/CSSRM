from ..structures import Bloxlink, Arguments # pylint: disable=import-error, no-name-in-module
from ..exceptions import CancelCommand # pylint: disable=import-error, no-name-in-module
from ..constants import DEFAULTS # pylint: disable=import-error, no-name-in-module
import discord
import re

parse_message = Bloxlink.get_module("commands", attrs="parse_message")
fetch = Bloxlink.get_module("utils", attrs="fetch")
get_guild_value = Bloxlink.get_module("cache", attrs=["get_guild_value"])


@Bloxlink.module
class MessageEvent:
	def __init__(self):
		self.domain_regex = re.compile("(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z0-9][a-z0-9-]{0,61}[a-z0-9]")

	async def __setup__(self):
		@Bloxlink.event
		async def on_message(message):
			author = message.author

			if (author.bot or not message.channel or Arguments.in_prompt(author)) or (message.guild and message.guild.unavailable):
				return

			if message.guild:
				# anti-phish check
				anti_phish = await get_guild_value(message.guild, ["antiPhish", DEFAULTS.get("antiPhish")])
				if anti_phish:
					domain_match = self.domain_regex.search(message.content)
					if domain_match:
						json_data, response = await fetch("https://anti-fish.bitflow.dev/check", "GET",
													headers={"User-Agent": "Bloxlink (https://blox.link)"},
													json=True, raise_on_failure=False, body={
														"message": message.content
													})
						if response.status == 200 and json_data.get("match") is True:
							try:
								await message.delete()
							except (discord.errors.Forbidden, discord.errors.NotFound):
								pass

							return

			try:
				await parse_message(message)
			except CancelCommand:
				pass
