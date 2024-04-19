"""
MCFetch is a package for working with Minecraft player data.

This package provides tools for fetching player data from the Mojang API,
including player names, UUIDs, and skins. It is a fork of the mcuuid package
that cleans up the code, updates it to be more modern and reliable,
and fixes KeyErrors by using .get().

To use this package, simply import it and create a
`FetchPlayer` object with the player's name or UUID:

```python
from mcfetch import FetchPlayer

player = FetchPlayer(name='Notch')
print(player.name)
print(player.uuid)
```
"""

name = "mcfetch"

from .mcfetch import *
from .asyncmcfetch import *
from .tools import *

__all__ = [
    'mcfetch',
    'asyncmcfetch'
]
