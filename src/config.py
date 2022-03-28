from os import environ as env
from resources.constants import RELEASE, IS_DOCKER # pylint: disable=import-error, no-name-in-module, no-name-in-module


WEBHOOKS = {
	"LOGS":  "", # discord webhook link
	"ERRORS": "" # discord webhook link
}


REACTIONS = { # discord emote mention strings
	"LOADING": "<a:BloxlinkLoading:530113171734921227>",
	"DONE": "<:BloxlinkSuccess:506622931791773696>",
	"DONE_ANIMATED": "<a:BloxlinkDone:528252043211571210>",
	"ERROR": "<:BloxlinkError:506622933226225676>",
	"VERIFIED": "<a:Verified:734628839581417472>",
	"BANNED": "<:ban:476838302092230672>",
	"RED": "<:red:881780174151110656>",
	"REPLY": "<:Reply:872019019677450240>",
	"REPLY_END": ":ReplyCont:872018974831968259>",
	"GREEN": "<:green:881783400632037426>",
	"BLANK": "<:blank:881783214014885908>"
}


BLOXLINK_GUILD = RELEASE == "LOCAL" and 439265180988211211 or 372036754078826496

BOTS = {
	"PRO": 469652514501951518,
	"MAIN": 426537812993638400,
	"CANARY": 957157213707849781,
	"LOCAL": 454053406471094282
}

MONGO_CONNECTION_STRING = "mongodb+srv://mongodb.com" # MongoDB connection string
MONGO_DB = "bloxlink" # the main collection name

REDIS_HOST = "redis"
REDIS_PORT = 6379
REDIS_PASSWORD = None

TOKEN = None
