import json
import random

import statalib as lib


def random_tip_message(discord_id: int):
    """
    Chooses a random message to send if the user doesnt have tip bypass perms
    :param discord_id: the discord id of the respective user
    """
    if lib.permissions.has_access(discord_id, 'no_tips'):
        return None

    if random.choice(([False]*5) + ([True]*2)):  # 2 in 7 chance
        try:
            with open(f'{lib.REL_PATH}/bot/tips.json', 'r') as datafile:
                messages = json.load(datafile).get('tip_messages')

            if messages:
                return random.choice(messages)
        except (FileNotFoundError, json.JSONDecodeError):
            pass
    return None
