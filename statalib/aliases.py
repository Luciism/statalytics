from typing import NewType


# Username of a minecraft player
PlayerName = NewType('PlayerName', str)

# UUID of a minecraft player
PlayerUUID = NewType('PlayerUUID', str)

# Dynamic identifier of a player (username, uuid, or linked discord id)
PlayerDynamic = NewType('PlayerDynamic', str)
