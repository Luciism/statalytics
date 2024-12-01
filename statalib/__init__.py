"""
Statalib is the shared library used by all services.

It contains utilities for managing accounts, making requests,
loading assets, calculating statistics, session stats, themes, and more.
"""

from . import rotational_stats as rotational_stats
from . import mcfetch
from . import loggers
from . import shared_views
from . import hypixel
from . import accounts

from .assets import ASSET_LOADER as ASSET_LOADER
from .cfg import *
from .errors import *
from .functions import *
from .sessions import *
from .autocomplete import *
from .handlers import *
from .network import *
from .aliases import *


__all__ = [
    'accounts',
    'calctools',
    'errors',
    'functions',
    'historical',
    'linking',
    'themes',
    'autocomplete',
    'sessions',
    'mcfetch',
    'subscriptions'
    'network',
    'permissions',
    'aliases',
    'loggers',
    'shared_views',
    'hypixel'
]
