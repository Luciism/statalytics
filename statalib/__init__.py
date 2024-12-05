"""
Statalib is the shared library used by all services.

It contains utilities for managing accounts, making requests,
loading assets, calculating statistics, session stats, themes, and more.
"""

from . import accounts
from . import db
from . import errors
from . import handlers
from . import hypixel
from . import loggers
from . import mcfetch
from . import network
from . import rotational_stats as rotational_stats
from . import sessions
from . import shared_views
from . import usage

from .aliases import *
from .assets import ASSET_LOADER
from .cfg import config
from .functions import *


__all__ = [
    'accounts',
    'db',
    'ASSET_LOADER',
    'config',
    'errors',
    'handlers',
    'hypixel',
    'loggers',
    'mcfetch',
    'network',
    'rotational_stats',
    'sessions',
    'shared_views',
    'usage',
]
