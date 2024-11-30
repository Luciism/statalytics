"""Type aliases."""

from typing import NewType


PlayerName = NewType('PlayerName', str)
"Username of a minecraft player."

PlayerUUID = NewType('PlayerUUID', str)
"UUID of a minecraft player."

PlayerDynamic = NewType('PlayerDynamic', str)
"Dynamic identifier of a player (username, UUID, or linked Discord ID)."
