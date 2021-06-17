from ..structures.Bloxlink import Bloxlink # pylint: disable=import-error


@Bloxlink.event
async def on_ready():
    Bloxlink.log(f"Logged in as {Bloxlink.user.name}")
