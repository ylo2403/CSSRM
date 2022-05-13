import discord


class Permissions(discord.Permissions):
    """Contains permission attributes for commands"""

    def __init__(self, function=None, **kwargs):
        self.function = function
        self.developer_only = False
        self.premium = False

        self.allow_bypass = False

        super().__init__(**kwargs)
