import os
import json
import random
import asyncio

import discord
from discord.utils import MISSING

from ..functions import REL_PATH
from ..permissions import has_access
from ..views.modes import ModesView


def discord_message(discord_id):
    """
    Chooses a random message to send if the user doesnt have tip bypass perms
    :param discord_id: the discord id of the respective user
    """
    if has_access(discord_id, 'no_tips'):
        return None

    if random.choice(([False]*5) + ([True]*2)):  # 2 in 7 chance
        try:
            with open(f'{REL_PATH}/database/discord_messages.json', 'r') as datafile:
                messages = json.load(datafile).get('active_messages')
            if messages:
                return random.choice(messages)
        except (FileNotFoundError, json.JSONDecodeError):
            pass
    return None


async def handle_modes_renders(
    interaction: discord.Interaction,
    func: object,
    kwargs: dict,
    message=None,
    custom_view: discord.ui.View=None
) -> None:
    """
    Renders and sends all modes to discord for the selected render
    :param interaction: the relative discord interaction object
    :param func: the function object to render with
    :param kwargs: the keyword arguments needed to render the image
    :param message: the message to send to discord with the image
    :param view: a discord view to merge with the sent view
    """
    if not message:
        message = discord_message(interaction.user.id)

    os.makedirs(f'{REL_PATH}/database/rendered/{interaction.id}')
    await func(mode="Overall", **kwargs)
    view = ModesView(
        inter=interaction,
        mode='Select a mode'
    )

    if custom_view is not None:
        for child in custom_view.children:
            view.add_item(child)

    image = discord.File(
        f"{REL_PATH}/database/rendered/{interaction.id}/overall.png")
    try:
        await interaction.edit_original_response(
            content=message, attachments=[image], view=view
        )
    except discord.errors.NotFound:
        return

    await asyncio.gather(
        func(mode="Solos", **kwargs),
        func(mode="Doubles", **kwargs),
        func(mode="Threes", **kwargs),
        func(mode="Fours", **kwargs),
        func(mode="4v4", **kwargs),
    )
