from ...structures.Bloxlink import Bloxlink # pylint: disable=no-name-in-module, import-error
import discord


@Bloxlink.module
class Binds(Bloxlink.Module):
    def __init__(self):
        pass

    async def get_linked_group_ids(self, guild):
        guild_data = await self.r.table("guilds").get(str(guild.id)).run() or {}

        role_binds = guild_data.get("roleBinds") or {}
        group_ids  = guild_data.get("groupIDs") or {}


        return set(group_ids.keys()).union(set(role_binds.get("groups", {}).keys()))


    async def update_user(self, user, guild):
        pass
