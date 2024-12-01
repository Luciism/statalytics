import time
import typing

import discord
from discord import app_commands

import statalib as lib
from statalib.accounts import Account


def generic_command_cooldown(
    interaction: discord.Interaction
) -> typing.Optional[app_commands.Cooldown]:
    """
    Gets interaction cooldown based on subscription and voting status.
    Cooldowns can be managed in the `config.json` file

    Paramaters will be handled automatically by discord.py
    """
    # If the user bypasses the cooldown
    if Account(interaction.user.id).permissions.has_access("cooldown_bypass"):
        return app_commands.Cooldown(1, 0.0)

    # If the user has voted recently
    voting_data = lib.accounts.Account(interaction.user.id).voting.load()

    if voting_data.last_vote:
        hours_since_voted = (time.time() - voting_data.last_vote) / 3600
        rewards_duration = lib.config('global.voting.reward_duration_hours')

        if (hours_since_voted < rewards_duration):
            return app_commands.Cooldown(1, 1.75)

    # Default configured cooldown
    cooldown_data = Account(interaction.user.id).subscriptions\
        .get_subscription().package_property("generic_command_cooldown", {})

    return app_commands.Cooldown(
        rate=cooldown_data.get('rate', 1),
        per=cooldown_data.get('per', 3.5)
    )
