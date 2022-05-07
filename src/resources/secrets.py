from os import environ as env
import config


VALID_SECRETS = ("REDIS_HOST", "REDIS_PORT", "REDIS_PASSWORD",
                "TOKEN", "SENTRY_URL", "DBL_KEY", "TOPGG_KEY", "PROXY_URL", "IMAGE_SERVER_URL",
                "IMAGE_SERVER_AUTH", "MONGO_CONNECTION_STRING", "MONGO_CA_FILE")



for secret in VALID_SECRETS:
    globals()[secret] = env.get(secret) or getattr(config, secret, "")
