"""
Module for handling API requests to Hypixel as well as skin model fetching.
"""

import asyncio
import logging
from typing import Any, Literal
from os import getenv
from json import JSONDecodeError
from http.client import RemoteDisconnected

from aiohttp_client_cache.response import CachedResponse
from requests import ReadTimeout, ConnectTimeout
from aiohttp import ClientError, ClientSession, ContentTypeError
from aiohttp_client_cache import CachedSession, SQLiteBackend

from .cfg import config
from .common import REL_PATH
from .errors import HypixelInvalidResponseError, HypixelRateLimitedError
from .aliases import HypixelData, PlayerUUID
from .rotational_stats import async_reset_rotational_stats_if_whitelisted


logger = logging.getLogger('statalytics')

stats_session = SQLiteBackend(
    cache_name=f'{REL_PATH}/.cache/stats_cache', expire_after=300)

skin_session = SQLiteBackend(
    cache_name=f'{REL_PATH}/.cache/skin_cache', expire_after=900)

mojang_session = SQLiteBackend(
    cache_name=f'{REL_PATH}/.cache/mojang_cache', expire_after=60)


SkinStyle = Literal[
    'face', 'front', 'frontfull', 'head',
    'bust', 'full', 'skin', 'processedskin'
]


async def __make_hypixel_request(
    session: ClientSession | CachedSession,
    uuid: str
) -> dict:
    api_key = getenv('API_KEY_HYPIXEL')

    options = {
        'url': f"https://api.hypixel.net/player?uuid={uuid}",
        'headers': {"API-Key": api_key},
        'timeout': 5
    }

    # fetch hypixel data
    res = await session.get(**options)
    hypixel_data = await res.json()

    # reset trackers using the data if they are due
    asyncio.ensure_future(
        async_reset_rotational_stats_if_whitelisted(uuid, hypixel_data)
    )

    return hypixel_data


async def fetch_hypixel_data(
    uuid: PlayerUUID,
    cache: bool = True,
    cached_session: SQLiteBackend = stats_session,
    retries: int = 3,
    retry_delay: int = 5
) -> HypixelData:
    """
    Fetch a player's Hypixel data from Hypixel's API.
    Supports caching and request retry system.

    :param uuid: The player UUID of the respective player.
    :param cache: Whether or not to use the cache.
    :param cached_session: Use a custom cache instead of the default stats cache.
    :param retries: The number of retries in before terminating the request.
    :param retry_delay: The delay (in seconds) between request retries.
    :return dict: The Hypixel API player data response.
    """
    for attempt in range(retries + 1):
        try:
            if not cache:
                async with ClientSession() as session:
                    return await __make_hypixel_request(session, uuid)

            async with CachedSession(cache=cached_session) as session:
                return await __make_hypixel_request(session, uuid)

        except (ReadTimeout, ConnectTimeout, TimeoutError, asyncio.TimeoutError,
                JSONDecodeError, RemoteDisconnected, ContentTypeError) as exc:
            if attempt < retries:
                logger.warning(
                    f"Hypixel request failed. Retrying in {retry_delay} seconds...")
                await asyncio.sleep(retry_delay)
            else:
                raise HypixelInvalidResponseError(
                    "Maximum number of retries exceeded.") from exc


async def fetch_hypixel_data_rate_limit_safe(
    uuid: PlayerUUID,
    cache: bool = True,
    cached_session: SQLiteBackend = stats_session,
    retries: int = 3,
    retry_delay: int = 5,
    attempts=5,
    attempt_delay=20
) -> HypixelData:
    """
    Rate limit safe version of `~fetch_hypixel_data()`.

    :param uuid: The player UUID of the respective player.
    :param cache: Whether or not to use the cache.
    :param cached_session: Use a custom cache instead of the default stats cache.
    :param retries: The number of retries in the case of failed network requests.
    :param retry_delay: Delay (in seconds) between failed network request retries.
    :param attempts: The amount of attempts to make if you are rate limited.
    :param attempt_delay: Delay (in seconds) between attempts made if rate limited.
    :return dict: The Hypixel API player data response.
    """
    for attempt in range(attempts + 1):
        hypixel_data = await fetch_hypixel_data(
            uuid, cache, cached_session, retries, retry_delay)

        if not hypixel_data.get('success') and hypixel_data.get('throttle'):
            if attempt < attempts:
                logger.warning(
                    'We are being rate limited by hypixel. '
                    f'Retrying in {attempt_delay} seconds...')
                await asyncio.sleep(attempt_delay)
            else:
                raise HypixelRateLimitedError('Maximum number of retries exceeded.')

        elif hypixel_data.get('success'):
            return hypixel_data
    return hypixel_data


def skin_from_file(skin_type: str='bust') -> bytes:
    """Load a steve skin player model from file."""
    with open(f'{REL_PATH}/assets/steve_{skin_type}.png', 'rb') as skin:
        return skin.read()


async def fetch_skin_model(
    uuid: PlayerUUID,
    size: int,
    style: SkinStyle='bust'
) -> bytes:
    """
    Attempt to fetch a 3D skin model from Visage.
    If something goes wrong, a steve skin will returned.

    :param uuid: The player UUID of the respective player.
    :param size: The image size in pixels.
    :param style: The skin style to use.
    :return bytes: The skin model as bytes.
    """
    options = {
        'url': f'https://visage.surgeplay.com/{style}/{size}/{uuid}',
        'timeout': 5,
        'headers': {
            'User-Agent': f'Statalytics {config("apps.bot.version")}'
        }
    }

    try:
        async with CachedSession(cache=skin_session) as session:
            res_content = (await session.get(**options)).content
            return await res_content.read()

    # except (ReadTimeout, ConnectTimeout, TimeoutError, asyncio.TimeoutError):
    except Exception:  # shit just wasnt working idk why
        return skin_from_file()



