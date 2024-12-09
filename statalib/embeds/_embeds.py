from .help import HelpEmbeds
from .misc import MiscEmbeds
from .premium import PremiumEmbeds
from .settings import SettingsEmbeds
from .problems import ProblemsEmbeds


class Embeds:
    help = HelpEmbeds
    misc = MiscEmbeds
    premium = PremiumEmbeds
    settings = SettingsEmbeds
    problems = ProblemsEmbeds

__all__ = [
    "Embeds",
    "HelpEmbeds",
    "MiscEmbeds",
    "PremiumEmbeds",
    "SettingsEmbeds",
    "ProblemsEmbeds",
]
