import os
import json
import random

import discord

from ..functions import REL_PATH
from ..subscriptions import get_subscription
from ..views.modes import ModesView


def discord_message(discord_id):
    """
    Chooses a random message to send if the discord id has no subscription
    :param discord_id: the discord id of the respective user
    """
    if get_subscription(discord_id):
        return None

    if random.choice(([False]*5) + ([True]*2)): # 2 in 7 chance
        with open(f'{REL_PATH}/database/discord_messages.json', 'r') as datafile:
            data = json.load(datafile)
        return random.choice(data['active_messages'])
    return None


async def handle_modes_renders(interaction: discord.Interaction,
                               func: object, kwargs: dict, message=None):
    """
    Renders and sends all modes to discord for the selected render
    :param interaction: the relative discord interaction object
    :param func: the function object to render with
    :param kwargs: the keyword arguments needed to render the image
    :param message: the message to send to discord with the image
    """
    if not message:
        message = discord_message(interaction.user.id)

    os.makedirs(f'{REL_PATH}/database/rendered/{interaction.id}')
    await func(mode="Overall", **kwargs)
    view = ModesView(user=interaction.user.id, inter=interaction, mode='Select a mode')
    try:
        await interaction.edit_original_response(
            content=message,
            attachments=[
                discord.File(f"{REL_PATH}/database/rendered/{interaction.id}/overall.png")],
            view=view
        )
    except discord.errors.NotFound:
        return

    await func(mode="Solos", **kwargs)
    await func(mode="Doubles", **kwargs)
    await func(mode="Threes", **kwargs)
    await func(mode="Fours", **kwargs)
    await func(mode="4v4", **kwargs)
