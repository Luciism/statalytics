import asyncio
import logging
from typing import Literal
from os import getenv
from json import JSONDecodeError
from http.client import RemoteDisconnected

from requests import ReadTimeout, ConnectTimeout
from aiohttp import ClientSession
from aiohttp_client_cache import CachedSession, SQLiteBackend

from .functions import REL_PATH
from .errors import HypixelInvalidResponseError, HypixelRateLimitedError
from .aliases import PlayerUUID

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


async def fetch_hypixel_data(
    uuid: PlayerUUID,
    cache: bool = True,
    cached_session: SQLiteBackend = stats_session,
    retries: int = 3,
    retry_delay: int = 5
) -> dict:
    """
    Fetch a user's Hypixel data from Hypixel's
    API with retries and delay between retries.
    :param uuid: The UUID of the user's data to fetch.
    :param cache: Whether to use caching or not.
    :param cached_session: Use a custom cache instead of the default stats cache.
    :param retries: Number of retries in case of a failed request.
    :param retry_delay: Delay (in seconds) between retries.
    """
    api_key = getenv('API_KEY_HYPIXEL')

    options = {
        'url': f"https://api.hypixel.net/player?uuid={uuid}",
        'headers': {"API-Key": api_key},
        'timeout': 5
    }
    for attempt in range(retries + 1):
        try:
            if not cache:
                async with ClientSession() as session:
                    return await (await session.get(**options)).json()

            async with CachedSession(cache=cached_session) as session:
                return await (await session.get(**options)).json()

        except (ReadTimeout, ConnectTimeout, TimeoutError, asyncio.TimeoutError,
                JSONDecodeError, RemoteDisconnected) as exc:
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
) -> dict:
    """
    Wrapper around `fetch_hypixel_data` that is rate limit safe.
    5 attempts will be made with a 20 second delay if rate limited

    Fetch a user's Hypixel data from Hypixel's API
    with retries and delay between retries.
    :param uuid: The UUID of the user's data to fetch.
    :param cache: Whether to use caching or not.
    :param cached_session: Use a custom cache instead of the default stats cache.
    :param retries: Number of retries in case of a failed network request.
    :param retry_delay: Delay (in seconds) between failed network request retries.
    :param attempts: The amount of attempts to make if you are rate limited.
    :param attempt_delay: Delay (in seconds) between attempts made if rate limited.
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
    """Loads a steve skin from file"""
    with open(f'{REL_PATH}/assets/steve_{skin_type}.png', 'rb') as skin:
        return skin.read()


async def fetch_skin_model(
    uuid: PlayerUUID,
    size: int,
    style: SkinStyle='bust'
) -> bytes:
    """
    Fetches a 3d skin model visage.surgeplay.com
    If something goes wrong, a steve skin will returned
    :param uuid: The uuid of the relative player
    :param size: The skin render size in pixels
    """
    options = {
        'url': f'https://visage.surgeplay.com/{style}/{size}/{uuid}',
        'timeout': 5
    }
    try:
        async with CachedSession(cache=skin_session) as session:
            res_content = (await session.get(**options)).content
            return await res_content.read()

    # except (ReadTimeout, ConnectTimeout, TimeoutError, asyncio.TimeoutError):
    except Exception:  # shit just wasnt working idk why
        skin_model = skin_from_file()
    return skin_model
