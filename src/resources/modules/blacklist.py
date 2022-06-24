from ..structures import Bloxlink # pylint: disable=import-error, no-name-in-module
import json
import logging

cache_get, get_guild_value = Bloxlink.get_module("cache", attrs=["get", "get_guild_value"])


@Bloxlink.module
class Blacklist(Bloxlink.Module):
    def __init__(self):
        self.blacklist = {
            "users": {},
            "guilds": {},
            "robloxAccounts": {}
        }

    async def __setup__(self):
        try:
            with open("src/data/blacklist.json", "r+") as f:
                blacklist_json = json.load(f)

                for user_id, user_data in blacklist_json["users"].items():
                    reason = user_data.get("reason") or "This user is prohibited from using Bloxlink for violating our rules."

                    self.blacklist["users"][user_id] = reason

                    for roblox_id in user_data.get("robloxAccounts", []):
                        self.blacklist["robloxAccounts"][roblox_id] = reason

                    for guild_id in user_data.get("guilds", []):
                        self.blacklist["guilds"][guild_id] = reason

                for guild_id, reason in blacklist_json["guilds"].items():
                    self.blacklist["guilds"][guild_id] = reason

        except FileNotFoundError:
            logging.error("Blacklist file not found.")

    async def get_restriction(self, typex, idx, guild=None, roblox_user=None):
        idx = str(idx)

        # server restrictions
        if guild:
            restrictions = await get_guild_value(guild, "restrictions")

            if restrictions:
                restriction = restrictions.get(typex, {}).get(idx, {})

                if restriction:
                    return restriction.get("reason") or "This server has restricted you from verifying."

                if roblox_user:
                    for restricted_group_id, restricted_group in restrictions.get("groups", {}).items():
                        group = roblox_user.groups.get(restricted_group_id)

                        if group:
                            return restricted_group.get("reason") or f"This server has prevented your group {group.name} from verifying."


        # bloxlink-wide restrictions
        return self.blacklist[typex].get(idx)
