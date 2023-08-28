import time
import logging
from typing import Literal
from os import getenv
from json import JSONDecodeError
from http.client import RemoteDisconnected

from requests import ReadTimeout, ConnectTimeout
from aiohttp import ClientSession
from aiohttp_client_cache import CachedSession, SQLiteBackend

from .functions import REL_PATH
from .errors import HypixelInvalidResponseError
from .aliases import PlayerUUID


historic_cache = SQLiteBackend(
    cache_name=f'{REL_PATH}/.cache/historic_cache', expire_after=300)

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
    Fetch a user's Hypixel data from Hypixel's API with retries and delay between retries.
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

        except (ReadTimeout, ConnectTimeout,
                JSONDecodeError, RemoteDisconnected) as exc:
            if attempt < retries:
                logging.warning(
                    f"Hypixel request failed. Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                raise HypixelInvalidResponseError(
                    "Maximum number of retries exceeded.") from exc


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
        'timeout': 3
    }
    try:
        async with CachedSession(cache=skin_session) as session:
            res_content = (await session.get(**options)).content
            return await res_content.read()

    except (ReadTimeout, ConnectTimeout):
        skin_res = skin_from_file()
    return skin_res
