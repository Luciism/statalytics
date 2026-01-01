from dataclasses import dataclass
from typing import Any 

from .values import BedwarsQualifyingValueFormatter

from ...aliases import HypixelPlayerData
from ..ranks import RankInfo, get_rank_info

@dataclass(frozen=True)
class LeaderboardInfo:
    """The information that describes the leaderboard."""
    path: str
    "The ID of the leaderboard for the gamemode."
    prefix: str
    "Additional context for the title."
    title: str
    "The human-friendly leaderboard type."
    location: tuple[int, int, int]=(0, 0, 0)
    "Three random numbers???"


@dataclass(frozen=True)
class LeaderboardData:
    """Represents the data for a leaderboard."""
    info: LeaderboardInfo
    "The information that describes the leaderboard."
    count: int
    "The amount of leaders."
    leaders: tuple[str, ...]
    "The player UUIDs of the leaderboard players."

    @staticmethod
    def build(data: dict[str, Any]) -> 'LeaderboardData':
        """Build a new `LeaderboardData` object from response data."""
        return LeaderboardData(
            info=LeaderboardInfo(
                path=data["path"],
                prefix=data["prefix"],
                title=data["title"],
                location=tuple([int(pos) for pos in data["location"].split(",")]),
            ),
            count=data["count"],
            leaders=tuple(data["leaders"])
        )

def extract_data_using_path(data: dict[str, Any], path: str) -> int:  # Could be Any
    """
    Return the data nested in a dictionary at a given path (joined by `.`)

    Eg:
    ```
    >>> extract_data_using_value_path(data={"a": {"b": {"c": 1}}}, path="a.b.c")
    1
    ```

    :param data: The data to extract a value from.
    :param path: The dot delimited path to the value.
    """
    if path:
        for key in path.split('.'):
            data = data[key]

    return data


@dataclass
class LeaderboardPlayerEntry:
    """Data for a leaderboard player entry."""
    uuid: str
    "The UUID of the leaderboard player."
    username: str
    "The username of the leaderboard player."
    rank_info: RankInfo
    "The rank information of the leaderboard player."
    value: str 
    "The leaderboard qualifying value achieved by the player."

    @staticmethod
    def build(player_data: HypixelPlayerData, leaderboard: LeaderboardData) -> 'LeaderboardPlayerEntry':
        """
        Build a new `LeaderPlayerEntry` object from hypixel player data.
        
        :param player_data: The hypixel player data of the leaderboard player.
        :param value_path: The dot (.) delimited path to the leaderboard qualifying value.
        """
        return LeaderboardPlayerEntry(
            uuid=player_data["uuid"],
            username=player_data["displayname"],
            rank_info=get_rank_info(player_data),
            value=BedwarsQualifyingValueFormatter(player_data).call_formatter(leaderboard.info.path)
        )


@dataclass
class GuildLiveLeaderboard:
    guild_id: int
    channel_id: int
    leaderboard_path: str
    message_id: int



LEADERBOARD_TYPES = {
    "bedwars_level": LeaderboardInfo("bedwars_level", "Current", "Level", (0, 0, 0)),
    "wins_new": LeaderboardInfo("wins_new", "Overall", "Wins", (0, 0, 0)),
    "final_kills_new": LeaderboardInfo("final_kills_new", "Overall", "Final Kills", (0, 0, 0))
}

