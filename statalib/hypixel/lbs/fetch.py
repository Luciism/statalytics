import os
import time
import asyncio
from typing import Any, AsyncGenerator
from json import JSONDecodeError

from aiohttp import ClientResponse, ClientSession, ClientError, ClientTimeout
from aiohttp_client_cache import SQLiteBackend
from aiohttp_client_cache.response import CachedResponse
from aiohttp_client_cache.session import CachedSession

from ..utils import get_player_dict
from ...common import REL_PATH
from .models import LeaderboardData, LeaderboardPlayerEntry



async def _fetch_hypixel_leaderboards(attempts: int=3, _attempt: int=1) -> dict[str, Any]:
    try:
        async with ClientSession() as session:
            res = await session.get("https://api.hypixel.net/v2/leaderboards", headers={
                "Api-Key": os.getenv("API_KEY_HYPIXEL")
            }, timeout=5)

            if not res.ok:
                raise ClientError(f"Got unexpected non-ok status: {res.status}")

            data: dict[str, Any] = await res.json()
            return data
    except (ClientError, TimeoutError, JSONDecodeError):
        if _attempt == attempts:
            raise

        await asyncio.sleep(2)
        return await _fetch_hypixel_leaderboards(attempts, _attempt + 1)


def deserialize_bedwars_leaderboard_data(lb_data: dict[str, Any]) -> list[LeaderboardData]:
    bedwars_leaderboards = lb_data["leaderboards"]["BEDWARS"]
    return [LeaderboardData.build(lb) for lb in bedwars_leaderboards]


async def fetch_bedwars_leaderboards() -> list[LeaderboardData]:
    data = await _fetch_hypixel_leaderboards()
    return deserialize_bedwars_leaderboard_data(data)

player_session = SQLiteBackend(
    cache_name=f'{REL_PATH}/database/.cache/hypixel_player_cache',
    expire_after=60*60*24
)

async def fetch_leaderboard_players(
    leaderboard: LeaderboardData
) -> AsyncGenerator[LeaderboardPlayerEntry, None]:
    last_req_ts = 0

    async with CachedSession(cache=player_session) as session:
        session: CachedSession

        for uuid in leaderboard.leaders:
            url = f"https://api.hypixel.net/player?uuid={uuid}" 

            cache_key = session.cache.create_key("GET", url)
            cached_res = await session.cache.get_response(cache_key)

            if not cached_res or cached_res.is_expired:
                # Production key: 600 requests per 300 seconds (5 minutes)
                # Don't want to max out, use 33% capacity instead
                max_sleep = 1.5  # Seconds
                reduce_by = time.time() - last_req_ts

                await asyncio.sleep(max(0, max_sleep - reduce_by))

            res: ClientResponse | CachedResponse = await session.get(
                url=url,
                headers={"API-Key": os.getenv("API_KEY_HYPIXEL")},
                timeout=ClientTimeout(5)
            )

            if res.from_cache is False:
                last_req_ts = time.time()

            hypixel_data = await res.json()
            player_data = get_player_dict(hypixel_data) 

            profile = LeaderboardPlayerEntry.build(player_data, leaderboard)
            yield profile

