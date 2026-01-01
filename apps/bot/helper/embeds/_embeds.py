"""Main module for embeds."""

from typing import final
from .help import HelpEmbeds
from .misc import MiscEmbeds
from .premium import PremiumEmbeds
from .settings import SettingsEmbeds
from .problems import ProblemsEmbeds
from .leaderboards import LeaderboardEmbeds


@final
class Embeds:  # pylint: disable=too-few-public-methods
    """Discord embeds for statalytics."""
    help = HelpEmbeds
    misc = MiscEmbeds
    premium = PremiumEmbeds
    settings = SettingsEmbeds
    problems = ProblemsEmbeds
    leaderboard = LeaderboardEmbeds

__all__ = [
    "Embeds",
    "HelpEmbeds",
    "MiscEmbeds",
    "PremiumEmbeds",
    "SettingsEmbeds",
    "ProblemsEmbeds",
    "LeaderboardEmbeds"
]
