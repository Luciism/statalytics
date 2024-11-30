"""Type aliases."""

from typing import NewType


PlayerName = NewType('PlayerName', str)
"Username of a minecraft player."

PlayerUUID = NewType('PlayerUUID', str)
"UUID of a minecraft player."

PlayerDynamic = NewType('PlayerDynamic', str)
"Dynamic identifier of a player (username, UUID, or linked Discord ID)."

HypixelData = NewType('HypixelData', dict)
"Raw data fetched from the Hypixel API."

HypixelPlayerData = NewType('HypixelPlayerData', dict)
"'player' key of raw data fetched from the Hypixel API."

BedwarsData = NewType('BedwarsData', dict)
"'player'>'stats'>'Bedwars' key of raw data fetched from the Hypixel API."
