from ..structures import Bloxlink # pylint: disable=import-error, no-name-in-module


cache_get, get_guild_value = Bloxlink.get_module("cache", attrs=["get", "get_guild_value"])


@Bloxlink.module
class Blacklist(Bloxlink.Module):
    async def get_restriction(self, type, id, guild=None, roblox_user=None):
        id = str(id)

        if guild:
            restrictions = await get_guild_value(guild, "restrictions")

            if restrictions:
                restriction = restrictions.get(type, {}).get(id, {})

                if restriction:
                    return restriction.get("reason") or "This server has restricted you from verifying."

                if roblox_user:
                    for restricted_group_id, restricted_group in restrictions.get("groups", {}).items():
                        group = roblox_user.groups.get(restricted_group_id)

                        if group:
                            return restricted_group.get("reason") or f"This server has prevented your group {group.name} from verifying."
        else:
            restriction = await cache_get(f"restrictions:global:{type}:{id}", primitives=True)

            if restriction is not None:
                if restriction:
                    return restriction

                return True
