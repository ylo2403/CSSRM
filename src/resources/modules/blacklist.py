from ..structures import Bloxlink # pylint: disable=import-error
from ..constants import RELEASE # pylint: disable=import-error
from config import RESTRICTIONS_TRELLO # pylint: disable=import-error, no-name-in-module
from time import time
import re


trello = Bloxlink.get_module("trello", attrs="trello")
cache_set, cache_get = Bloxlink.get_module("cache", attrs=["set", "get"])


@Bloxlink.module
class Blacklist(Bloxlink.Module):
    def __init__(self):
        self.option_regex = re.compile("(.+):(.+)")

        self.trello_board = None

    async def __setup__(self):
        await self.load_blacklist()

    async def get_restriction(self, type, id):
        restriction = await cache_get(f"restrictions:{type}:{id}", primitives=True)

        if restriction is not None:
            if restriction:
                return restriction

            return True

    async def parse_data(self, trello_list, directory):
        for card in await trello_list.get_cards():
            match = self.option_regex.search(card.name)

            if match:
                ID = match.group(2)
                desc = card.desc

                await cache_set(f"restrictions:{directory}:{ID}", desc)

    async def load_blacklist(self):
        if RELEASE in ("CANARY", "LOCAL"):
            restricted_users = await self.r.db("bloxlink").table("restrictedUsers").run()

            time_now = (time()) * 1000 # for compatibility with the Javascript Bloxlink API

            async for restricted_user in restricted_users:
                restrictions = restricted_user["restrictions"]

                for i, restriction in enumerate(list(restrictions)):
                    if restriction["expiry"] <= time_now:
                        try:
                            restrictions.pop(i)
                            restricted_user["restrictions"] = restrictions

                            await self.r.db("bloxlink").table("restrictedUsers").insert(restricted_user, conflict="update").run()
                        except IndexError:
                            pass
                    else:
                        if restriction["type"] in ("global", "bot"):
                            await cache_set(f"restrictions:discord_ids:{restricted_user['id']}", restriction["reason"])

                if not restrictions:
                    await self.r.db("bloxlink").table("restrictedUsers").get(restricted_user["id"]).delete().run()

            try:
                self.trello_board = await trello.get_board(RESTRICTIONS_TRELLO)
            except Exception:
                pass
            else:
                roblox_ids = await self.trello_board.get_list(lambda l: l.name == "Roblox Accounts")
                discord_ids = await self.trello_board.get_list(lambda l: l.name == "Discord Accounts")
                server_ids = await self.trello_board.get_list(lambda l: l.name == "Servers")

                await self.parse_data(roblox_ids, "roblox_ids")
                await self.parse_data(discord_ids, "discord_ids")
                await self.parse_data(server_ids, "guilds")

