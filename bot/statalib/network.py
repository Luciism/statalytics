import time
import logging
from os import getenv
from json import JSONDecodeError
from http.client import RemoteDisconnected

import requests
from requests import ReadTimeout, ConnectTimeout
from requests_cache import CachedSession

from .functions import to_thread, REL_PATH
from .errors import HypixelInvalidResponseError
from .aliases import PlayerUUID


historic_cache = CachedSession(
    cache_name=f'{REL_PATH}/.cache/historic_cache', expire_after=300)

stats_session = CachedSession(
    cache_name=f'{REL_PATH}/.cache/stats_cache', expire_after=300)

skin_session = CachedSession(
    cache_name=f'{REL_PATH}/.cache/skin_cache', expire_after=900)

mojang_session = CachedSession(
    cache_name=f'{REL_PATH}/.cache/mojang_cache', expire_after=60)


@to_thread
def fetch_hypixel_data(
    uuid: PlayerUUID,
    cache: bool = True,
    cache_obj: CachedSession = stats_session,
    retries: int = 3,
    retry_delay: int = 5
) -> dict:
    """
    Fetch a user's Hypixel data from Hypixel's API with retries and delay between retries.
    :param uuid: The UUID of the user's data to fetch.
    :param cache: Whether to use caching or not.
    :param cache_obj: Use a custom cache instead of the default stats cache.
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
                return requests.get(**options).json()
            return cache_obj.get(**options).json()

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


@to_thread
def fetch_skin_model(uuid: PlayerUUID, size: int) -> bytes:
    """
    Fetches a 3d skin model visage.surgeplay.com
    If something goes wrong, a steve skin will returned
    :param uuid: The uuid of the relative player
    :param size: The skin render size in pixels
    """
    try:
        skin_res = skin_session.get(
            f'https://visage.surgeplay.com/bust/{size}/{uuid}',
            timeout=3).content
    except (ReadTimeout, ConnectTimeout):
        skin_res = skin_from_file()
    return skin_res
