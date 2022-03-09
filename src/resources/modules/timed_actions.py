from ..structures.Bloxlink import Bloxlink # pylint: disable=import-error, no-name-in-module
from ..constants import CACHE_CLEAR # pylint: disable=import-error, no-name-in-module
import asyncio



cache_clear = Bloxlink.get_module("cache", attrs=["clear"])
load_blacklist = Bloxlink.get_module("blacklist", attrs=["load_blacklist"])
load_staff_members = Bloxlink.get_module("premium", attrs=["load_staff_members"])


@Bloxlink.module
class TimedActions(Bloxlink.Module):
    def __init__(self):
        pass

    async def __setup__(self):
        await Bloxlink.wait_until_ready()
        await self.timed_actions()


    async def timed_actions(self):
        while True:
            await cache_clear()

            try:
                await load_blacklist() # redis
                await load_staff_members() # redis
            except Exception as e:
                Bloxlink.error(e)

            await asyncio.sleep(CACHE_CLEAR * 60)
