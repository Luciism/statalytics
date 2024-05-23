from ..cfg import config
from ..subscriptions import SubscriptionManager
from ..functions import load_embeds


FALLBACK_MAX_LOOKBACK = 30  # Days


def get_max_lookback(discord_ids: list[int]) -> int | None:
    """
    Get the highest possible max historical rotational stats lookback
    value for a range of Discord user IDs.

    :param discord_ids: A list of Discord user IDs to find the max lookback for.
    :return: Number of days (int) or infinite lookback (None).
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
        SubscriptionManager(discord_id) \
            .get_subscription() \
            .package_property("max_lookback", FALLBACK_MAX_LOOKBACK)
        for discord_id in discord_ids
    ]

    # No limit
    if None in max_lookbacks:
        return None

    # Highest value
    return max(max_lookbacks)


def build_invalid_lookback_embeds(max_lookback) -> list:
    """
    Responds to a interaction with an max lookback exceeded message
    :param max_lookback: The maximum lookback the user had availiable
    """
    format_values = {
        'description': {
            'max_lookback': max_lookback
        },
        'fields': {
            0: {
                'value': {
                    'max_lookback': max_lookback
                }
            }
        }
    }
    embeds = load_embeds('max_lookback', format_values, color='primary')

    return embeds
