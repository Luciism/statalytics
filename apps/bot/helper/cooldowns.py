import time
import typing

import discord
from discord import app_commands

import statalib as lib


def generic_command_cooldown(
    interaction: discord.Interaction
) -> typing.Optional[app_commands.Cooldown]:
    """
    Gets interaction cooldown based on subscription and voting status.
    Cooldowns can be managed in the `config.json` file

    Paramaters will be handled automatically by discord.py
    """
    # if the user bypasses the cooldown
    if lib.has_access(interaction.user.id, 'cooldown_bypass'):
        return app_commands.Cooldown(1, 0.0)

    # If the user has voted recently
    voting_data = lib.get_voting_data(interaction.user.id)

    if voting_data:
        hours_since_voted = (time.time() - voting_data[3]) / 3600
        rewards_duration = lib.config('global.voting.reward_duration_hours')

        if (hours_since_voted < rewards_duration):
            return app_commands.Cooldown(1, 1.75)

    # default configured cooldown
    cooldown_data = lib.SubscriptionManager(interaction.user.id)\
        .get_subscription().package_property("generic_command_cooldown", {})

    return app_commands.Cooldown(
        rate=cooldown_data.get('rate', 1),
        per=cooldown_data.get('per', 3.5)
    )
