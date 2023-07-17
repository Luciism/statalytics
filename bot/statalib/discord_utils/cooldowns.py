import time
import typing

import discord
from discord import app_commands

from ..subscriptions import get_subscription
from ..functions import get_voting_data, get_config


def generic_command_cooldown(interaction: discord.Interaction
                         ) -> typing.Optional[app_commands.Cooldown]:
    """
    Gets interaction cooldown based on subscription and voting status.
    Subscription = 0 seconds
    Recent vote = 1.75
    Nothing = 3.5

    Paramaters will be handled automatically by discord.py
    """
    subscription = get_subscription(interaction.user.id)
    if subscription:
        return app_commands.Cooldown(1, 0.0)

    # If user has active vote rewards
    voting_data = get_voting_data(interaction.user.id)

    if voting_data:
        hours_since_voted = (time.time() - voting_data[3]) / 3600
        rewards_duration = get_config()['voter_reward_duration_hours']

        if (hours_since_voted < rewards_duration):
            return app_commands.Cooldown(1, 1.75)