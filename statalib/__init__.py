"""
Statalib is the shared library used by all services.

It contains utilities for managing accounts, making requests,
loading assets, calculating statistics, session stats, themes, and more.
"""

from . import (
    accounts,
    db,
    embeds,
    errors,
    fmt,
    handlers,
    hypixel,
    loggers,
    network,
    redis_ext,
    render,
    rotational_stats,
    sessions,
    shared_views,
    stats_snapshot,
    usage,
)
from .aliases import *
from .assets import ASSET_LOADER
from .cfg import config
from .common import MISSING, REL_PATH, Mode, ModesEnum, utc_now
from .embeds import Embeds
from .functions import *

__all__ = [
    "accounts",
    "db",
    "ASSET_LOADER",
    "config",
    "embeds",
    "Embeds",
    "errors",
    "fmt",
    "handlers",
    "hypixel",
    "loggers",
    "network",
    "render",
    "rotational_stats",
    "sessions",
    "stats_snapshot",
    "shared_views",
    "usage",
    "redis_ext",
    "REL_PATH",
    "MISSING",
    "utc_now",
    "Mode",
    "ModesEnum",
]
