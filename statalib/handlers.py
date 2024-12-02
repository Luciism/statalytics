"""Bot error handling functionality."""

import logging
from io import StringIO
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
) -> None:
    """
    Logs and sends an error message to the Discord error logs channel.

    :param client: The discord.py client object.
    :param error: The exception object for the error.
    :param metadata: Metadata mappings to include in the error message.
    """
    # Format and log the traceback.
    traceback_str = ''.join(
        format_exception(type(error), error, error.__traceback__))
    logger.error(traceback_str)

    # Don't send error messages if the client is not passed.
    if client is None:
        return

    # Wait until the client is ready before attempting to send.
    await client.wait_until_ready()
    channel = client.get_channel(
        config('global.support_server.channels.error_logs_channel_id'))

    tb_file = discord.File(
        fp=StringIO(traceback_str), filename="traceback.txt")

    await channel.send(
        content=
            f"Error: `{error}`\n" +
            "\n".join([f"{k}: `{v}`" for k, v in metadata.items()]) +
            "\nTraceback:",
        file=tb_file
    )

async def handle_hypixel_error(interaction: discord.Interaction) -> None:
    """Attempt to respond to a Hypixel API error."""
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
) -> None:
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
) -> None:
    embed = discord.Embed(
        title=
            f'An error occured running /{interaction.data["name"]}'
            if interaction.type == 2 else
            'An error occured while trying to complete your request.',
        description=
            f'```{error}```\nIf the problem persists, please '
            f'[get in touch]({config("global.links.support_server")})',
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
            "Invoked By": f"{interaction.user} ({interaction.user.id})",
            "Latency": f"{int(interaction.client.latency * 1000)}ms"
        }
    )


async def handle_interaction_errors(
    interaction: discord.Interaction,
    error: app_commands.AppCommandError
) -> None:
    """
    Handles all interaction related errors.

    :param interaction: The `discord.Interaction` object of the interaction.
    :param error: The exception object for the error that occured.
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
