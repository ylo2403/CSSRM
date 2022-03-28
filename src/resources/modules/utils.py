from os import listdir
from re import compile
from ..structures import Bloxlink # pylint: disable=import-error, no-name-in-module, no-name-in-module
from ..exceptions import RobloxAPIError, RobloxDown, RobloxNotFound, CancelCommand # pylint: disable=import-error, no-name-in-module, no-name-in-module
from ..constants import RELEASE, HTTP_RETRY_LIMIT # pylint: disable=import-error, no-name-in-module, no-name-in-module
from ..secrets import PROXY_URL # pylint: disable=import-error, no-name-in-module, no-name-in-module
from discord.errors import NotFound, Forbidden
from discord import Embed
from aiohttp.client_exceptions import ClientOSError, ServerDisconnectedError
from requests.utils import requote_uri
from async_timeout import timeout as a_timeout
import asyncio
import aiohttp
import json as json_


get_guild_value = Bloxlink.get_module("cache", attrs=["get_guild_value"])

@Bloxlink.module
class Utils(Bloxlink.Module):
    def __init__(self):
        self.option_regex = compile("(.+):(.+)")
        self.timeout = aiohttp.ClientTimeout(total=20)

    @staticmethod
    def get_files(directory):
        return [name for name in listdir(directory) if name[:1] != "." and name[:2] != "__" and name != "_DS_Store"]

    @staticmethod
    def coro_async(corofn, *args):
        # https://stackoverflow.com/questions/46074841/why-coroutines-cannot-be-used-with-run-in-executor
        loop = asyncio.new_event_loop()

        try:
            coro = corofn(*args)
            asyncio.set_event_loop(loop)

            return loop.run_until_complete(coro)

        finally:
            loop.close()

    @staticmethod
    async def suppress_timeout_errors(awaitable):
        try:
            return await awaitable
        except asyncio.TimeoutError:
            pass

    async def post_event(self, guild, event_name, text, color=None):
        log_channels = await get_guild_value(guild, "logChannels") or {}
        log_channel  = log_channels.get(event_name) or log_channels.get("all")

        if log_channel:
            text_channel = guild.get_channel(int(log_channel))

            if text_channel:
                embed = Embed(title=f"{event_name.title()} Event", description=text)
                embed.colour = color

                try:
                    await text_channel.send(embed=embed)
                except (Forbidden, NotFound):
                    pass

    async def fetch(self, url, method="GET", params=None, headers=None, body=None, text=False, json=True, bytes=False, raise_on_failure=True, retry=HTTP_RETRY_LIMIT, timeout=20, proxy=True):
        params  = params or {}
        headers = headers or {}
        new_json = {}
        proxied = False

        if text or bytes:
            json = False

        if proxy and PROXY_URL and "roblox.com" in url:
            old_url = url
            new_json["url"] = url
            new_json["data"] = body or {}
            url = PROXY_URL
            proxied = True
            method = "POST"

            if RELEASE == "LOCAL":
                print(f"{old_url} -> {url}")
        else:
            if RELEASE == "LOCAL":
                print(f"Making request to {url} with method {method}")

            new_json = body
            old_url = url

        url = requote_uri(url)

        for k, v in params.items():
            if isinstance(v, bool):
                params[k] = "true" if v else "false"

        try:
            async with a_timeout(timeout): # I noticed sometimes the aiohttp timeout parameter doesn't work. This is added as a backup.
                async with self.session.request(method, url, json=new_json, params=params, headers=headers, timeout=timeout) as response:
                    if proxied:
                        try:
                            response_json = await response.json()
                        except aiohttp.client_exceptions.ContentTypeError:
                            raise RobloxAPIError

                        response_body = response_json["req"]["body"]
                        response_status = response_json["req"]["status"]
                        response.status = response_status

                        if not isinstance(response_body, dict):
                            try:
                                response_body_json = json_.loads(response_body)
                            except:
                                pass
                            else:
                                response_body = response_body_json
                    else:
                        response_status = response.status
                        response_body = None

                    if raise_on_failure:
                        if response_status == 503:
                            raise RobloxDown
                        elif response_status == 404:
                            raise RobloxNotFound
                        elif response_status >= 400:
                            if proxied:
                                print(old_url, response_body, flush=True)
                            else:
                                print(old_url, await response.text(), flush=True)
                            raise RobloxAPIError

                        if json:
                            if not proxied:
                                try:
                                    response_body = await response.json()
                                except aiohttp.client_exceptions.ContentTypeError:
                                    raise RobloxAPIError

                            if isinstance(response_body, dict):
                                return response_body, response
                            else:
                                return {}, response

                    if text:
                        if proxied:
                            return str(response_body), response

                        text = await response.text()

                        return text, response

                    elif json:
                        if proxied:
                            if not isinstance(response_body, dict):
                                print("Roblox API Error: ", old_url, type(response_body), response_body, flush=True)

                                if raise_on_failure:
                                    raise RobloxAPIError

                            return response_body, response

                        try:
                            json = await response.json()
                        except aiohttp.client_exceptions.ContentTypeError:
                            print(old_url, await response.text(), flush=True)

                            raise RobloxAPIError

                        return json, response

                    elif bytes:
                        return await response.read(), response

                    return response

        except asyncio.TimeoutError:
            print(f"URL {old_url} timed out", flush=True)
            raise RobloxDown

    # async def fetch(self, url, method="GET", params=None, headers=None, json=None, body=None, text=True, bytes=False, raise_on_failure=True, retry=HTTP_RETRY_LIMIT, timeout=20):
    #     params  = params or {}
    #     headers = headers or {}

    #     url = requote_uri(url)

    #     if RELEASE == "LOCAL":
    #         Bloxlink.log(f"Making HTTP request: {url}")

    #     for k, v in params.items():
    #         if isinstance(v, bool):
    #             params[k] = "true" if v else "false"

    #     if bytes or json:
    #         text = False

    #     # if "roblox.com" in url:
    #     proxy = "aaa"
    #     # else:
    #     #     proxy = None

    #     try:
    #         async with a_timeout(timeout): # I noticed sometimes the aiohttp timeout parameter doesn't work. This is added as a backup.
    #             async with self.session.request(method, url, json=body, params=params, headers=headers, timeout=timeout, proxy=proxy) as response:
    #                 if response.status == 503:
    #                     raise RobloxDown

    #                 if raise_on_failure:
    #                     if response.status >= 500:
    #                         if retry != 0:
    #                             retry -= 1
    #                             await asyncio.sleep(1.0)

    #                             return await self.fetch(url, raise_on_failure=raise_on_failure, bytes=bytes, json=json, text=text, params=params, headers=headers, retry=retry, timeout=timeout)

    #                         raise RobloxAPIError

    #                     elif response.status == 400:
    #                         raise RobloxAPIError
    #                     elif response.status == 404:
    #                         raise RobloxNotFound

    #                 if bytes:
    #                     return await response.read(), response
    #                 elif text:
    #                     return await response.text(), response
    #                 elif json:
    #                     return await response.json(), response

    #     except ServerDisconnectedError:
    #         if retry != 0:
    #             return await self.fetch(url, retry=retry-1, raise_on_failure=raise_on_failure, bytes=bytes, json=json, text=text, params=params, headers=headers, timeout=timeout)
    #         else:
    #             raise ServerDisconnectedError

    #     except ClientOSError:
    #         # TODO: raise HttpError with non-roblox URLs
    #         raise RobloxAPIError

    #     except asyncio.TimeoutError:
    #         raise RobloxDown
