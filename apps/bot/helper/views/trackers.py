import discord

import statalib as lib

from .info import RotationalResettingInfoButton

def tracker_view() -> discord.ui.View:
    """Returns discord view with information on tracker resetting"""
    auto_reset_config: dict = lib.config('apps.bot.tracker_resetting.automatic') or {}
    is_whitelist_only = auto_reset_config.get('whitelist_only')

    # return resetting info view
    if is_whitelist_only:
        return RotationalResettingInfoButton()

    # return empty view
    return discord.ui.View()
