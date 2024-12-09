"""Rotational stats lookback functionality."""

from ..cfg import config
from ..accounts.subscriptions import AccountSubscriptions


FALLBACK_MAX_LOOKBACK = 30  # Days
"""Fallback value for maximum lookback duration (in days)."""


def get_max_lookback(discord_ids: list[int]) -> int | None:
    """
    Get the highest possible max historical rotational stats lookback
    value for a range of Discord user IDs.

    :param discord_ids: A list of Discord user IDs to find the max lookback for.
    :return int | None: The number of days (int) or infinite lookback (None).
    """
    if not discord_ids:
        try:
            # Get configured lookback of default package
            default_package = config("global.subscriptions.default_package")
            return config(
                f"global.subscriptions.packages.{default_package}.properties.max_lookback")
        except KeyError:
            return FALLBACK_MAX_LOOKBACK  # Fallback

    max_lookbacks: list[int | None] = [
        AccountSubscriptions(discord_id) \
            .get_subscription() \
            .package_property("max_lookback", FALLBACK_MAX_LOOKBACK)
        for discord_id in discord_ids
        if discord_id is not None
    ]

    # No limit
    if None in max_lookbacks:
        return None

    # Highest value
    return max(max_lookbacks)
