"""
Statalib is the shared library used by all services.

It contains utilities for managing accounts, making requests,
loading assets, calculating statistics, session stats, themes, and more.
"""

from . import accounts
from . import db
from . import embeds
from . import errors
from . import fmt
from . import handlers
from . import hypixel
from . import loggers
from . import network
from . import render
from . import redis_ext
from . import rotational_stats
from . import sessions
from . import shared_views
from . import usage

from .aliases import *
from .assets import ASSET_LOADER
from .cfg import config
from .common import REL_PATH, MISSING, utc_now, ModesEnum, Mode
from .embeds import Embeds
from .functions import *


__all__ = [
    'accounts',
    'db',
    'ASSET_LOADER',
    'config',
    'embeds',
    'Embeds',
    'errors',
    'fmt',
    'handlers',
    'hypixel',
    'loggers',
    'network',
    'render',
    'rotational_stats',
    'sessions',
    'shared_views',
    'usage',
    'redis_ext',
    'REL_PATH',
    'MISSING',
    'utc_now',
    'Mode',
    'ModesEnum'
]
