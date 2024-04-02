import time
import typing

import discord
from discord import app_commands

from ..subscriptions import get_user_property
from ..permissions import has_access
from ..cfg import config
from ..functions import get_voting_data


def generic_command_cooldown(
    interaction: discord.Interaction
) -> typing.Optional[app_commands.Cooldown]:
    """
    Gets interaction cooldown based on subscription and voting status.
    Cooldowns can be managed in the `config.json` file

    Paramaters will be handled automatically by discord.py
    """
    # if the user bypasses the cooldown
    if has_access(interaction.user.id, 'cooldown_bypass'):
        return app_commands.Cooldown(1, 0.0)

    # If the user has voted recently
    voting_data = get_voting_data(interaction.user.id)

    if voting_data:
        hours_since_voted = (time.time() - voting_data[3]) / 3600
        rewards_duration = config('voter_reward_duration_hours')

        if (hours_since_voted < rewards_duration):
            return app_commands.Cooldown(1, 1.75)

    # default configured cooldown
    cooldown_data: dict = get_user_property(
        interaction.user.id, 'generic_command_cooldown', {})

    return app_commands.Cooldown(
        rate=cooldown_data.get('rate', 1),
        per=cooldown_data.get('per', 3.5)
    )
