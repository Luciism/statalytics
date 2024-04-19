import logging
from io import StringIO
from os import getenv
from traceback import format_exception

import discord
from discord import app_commands

from .cfg import config
from .functions import load_embeds, get_embed_color
from .errors import (
    UserBlacklistedError,
    MissingPermissionsError,
    PlayerNotFoundError,
    SessionNotFoundError,
    MojangInvalidResponseError,
    HypixelInvalidResponseError
)


logger = logging.getLogger('statalytics')


async def log_error_msg(
    client: discord.Client,
    error: Exception,
    metadata: dict=None
):
    """
    Prints and sends an error message to discord error logs channel
    :param client: The discord.py client object
    :param error: The exception object for the error
    :param metadata: Metadata to include in the error message
    """
    traceback_str = ''.join(
        format_exception(type(error), error, error.__traceback__))
    logger.error(traceback_str)

    if getenv('ENVIRONMENT') == 'development' or not client:
        return

    await client.wait_until_ready()
    channel = client.get_channel(
        config('global.support_server.channels.error_logs_channel_id'))

    tb_file = discord.File(
        fp=StringIO(traceback_str), filename="traceback.txt")

    await channel.send(
        content=
            f"Error: `{error}`\n" +
            "\n".join([f"{k}: `{v}`\n" for k, v in metadata.items()]) +
            "Traceback:",
        file=tb_file
    )

async def handle_hypixel_error(interaction: discord.Interaction):
    try:
        embeds = load_embeds('hypixel_connection_error', color='danger')
        button = discord.ui.Button(
            label='API Status',
            url='https://status.hypixel.net/',
            emoji='<:hypixel:1126331001589731368>'
        )
        view = discord.ui.View().add_item(button)
        await interaction.edit_original_response(
            content=None, embeds=embeds, view=view)
    except discord.errors.NotFound:
        pass


async def _handle_mojang_error(interaction: discord.Interaction):
    try:
        embeds = load_embeds('mojang_error', color='danger')
        await interaction.edit_original_response(content=None, embeds=embeds)
    except discord.errors.NotFound:
        pass


async def _handle_cooldown_error(
    interaction: discord.Interaction,
    error: discord.app_commands.CommandOnCooldown
):
    format_values = {
        'description': {
            'retry_after': round(error.retry_after, 2)
        }
    }
    embeds = load_embeds('command_cooldown', format_values, color='warning')
    await interaction.response.send_message(embeds=embeds, ephemeral=True)


async def handle_remaining_tree_errors(
    interaction: discord.Interaction,
    error: Exception
):
    support_url = config('global.links.support_server')
    embed = discord.Embed(
        title=f'An error occured running /{interaction.data["name"]}',
        description=f'```{error}```\nIf the problem persists, '
                    f'please [get in touch]({support_url})',
        color=get_embed_color(embed_type='danger')
    )
    try:
        await interaction.edit_original_response(embed=embed)
    except discord.errors.NotFound:
        pass

    # print & log traceback to discord channel
    await log_error_msg(
        interaction.client,
        error,
        metadata={
            "Invoked By": f"{interaction.user} ({interaction.user.id})"
        }
    )


async def handle_interaction_errors(
    interaction: discord.Interaction,
    error: app_commands.AppCommandError
):
    """
    Handles all interaction related errors
    :param interaction: `discord.Interaction` object of the interaction
    :param error: the error that occured
    """

    if isinstance(error, PlayerNotFoundError):
        return

    if isinstance(error, SessionNotFoundError):
        return

    if isinstance(error, UserBlacklistedError):
        return

    if isinstance(error, MissingPermissionsError):
        return

    if isinstance(error, app_commands.CommandOnCooldown):
        await _handle_cooldown_error(interaction, error)
        return

    if isinstance(error, HypixelInvalidResponseError):
        await handle_hypixel_error(interaction)
        return

    if isinstance(error, MojangInvalidResponseError):
        await _handle_mojang_error(interaction)
        return

    await handle_remaining_tree_errors(interaction, error)
