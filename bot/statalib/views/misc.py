import discord

from ..cfg import config
from .info import TrackerResettingInfoButton


def tracker_view() -> discord.ui.View:
    """Returns discord view with information on tracker resetting"""
    auto_reset_config: dict = config('tracker_resetting.automatic') or {}
    is_whitelist_only = auto_reset_config.get('whitelist_only')

    # return resetting info view
    if is_whitelist_only:
        return TrackerResettingInfoButton()

    # return empty view
    return discord.ui.View()
