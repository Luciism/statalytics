import json
import logging
import random

from discord.abc import MISSING # pyright:ignore[reportAny]
import statalib as lib
from statalib.accounts import Account

logger = logging.getLogger(__name__)

def random_tip_message(discord_id: int) -> str | type[MISSING]:
    """
    Chooses a random message to send if the user doesnt have tip bypass perms
    :param discord_id: the discord id of the respective user
    """
    if Account(discord_id).permissions.has_access('no_tips'):
        return MISSING  # pyright:ignore[reportAny]

    tip_message_chance: int = lib.config("apps.bot.tip_message_chance")

    if random.randint(0, 100) < tip_message_chance:
        try:
            with open(f'{lib.REL_PATH}/bot/tips.json', 'r') as datafile:
                messages: list[str] = json.load(datafile)['tip_messages']

            if messages:
                return random.choice(messages)
        except (FileNotFoundError, json.JSONDecodeError, KeyError, TypeError) as exc:
            logger.warning(f"Failed to load tip messages: {exc}")
            pass

    return MISSING  # pyright:ignore[reportAny]
