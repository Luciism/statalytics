"""Type aliases."""

import typing
from typing import TypeAlias


PlayerName: TypeAlias = str
"Username of a minecraft player."

PlayerUUID: TypeAlias = str
"UUID of a minecraft player."

PlayerDynamic: TypeAlias = str | int
"Dynamic identifier of a player (username, UUID, or linked Discord ID)."

HypixelData: TypeAlias = dict[str, typing.Any]
"Raw data fetched from the Hypixel API."

HypixelPlayerData: TypeAlias = dict[str, typing.Any]
"'player' key of raw data fetched from the Hypixel API."

BedwarsData: TypeAlias = dict[str, typing.Any]
"'player'>'stats'>'Bedwars' key of raw data fetched from the Hypixel API."



__all__ = [
    'PlayerName',
    'PlayerUUID',
    'PlayerDynamic',
    'HypixelData',
    'HypixelPlayerData',
    'BedwarsData'
]
