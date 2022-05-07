from ..structures.Bloxlink import Bloxlink # pylint: disable=import-error, no-name-in-module
from ..constants import CACHE_CLEAR # pylint: disable=import-error, no-name-in-module
import asyncio



cache_clear = Bloxlink.get_module("cache", attrs=["clear"])


@Bloxlink.module
class TimedActions(Bloxlink.Module):
    def __init__(self):
        pass

    async def __setup__(self):
        await self.timed_actions()


    async def timed_actions(self):
        while True:
            await cache_clear()

            await asyncio.sleep(CACHE_CLEAR * 60)
