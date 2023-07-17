from os import getenv
from traceback import format_exception

import discord

from .functions import get_config, load_embeds
from .views.utils import LinkButton


async def log_error_msg(client: discord.Client, error: Exception):
    """
    Prints and sends an error message to discord error logs channel
    :param client: The discord.py client object
    :param error: The exception object for the error
    """
    traceback_str = ''.join(format_exception(type(error), error, error.__traceback__))
    print(traceback_str)

    if getenv('ENVIRONMENT') == 'development' or not client:
        return

    config = get_config()
    await client.wait_until_ready()
    channel = client.get_channel(config.get('error_logs_channel_id'))

    if len(traceback_str) > 1988:
        for i in range(0, len(traceback_str), 1988):
            substring = traceback_str[i:i+1988]
            await channel.send(f'```cmd\n{substring}\n```')
    else:
        await channel.send(f'```cmd\n{traceback_str[-1988:]}\n```')


async def handle_hypixel_error(interaction: discord.Interaction):
    try:
        embeds = load_embeds('hypixel_connection_error', color='danger')
        view = LinkButton(
            label='API Status',
            url="https://status.hypixel.net/",
            emoji='<:hypixel:1126331001589731368>'
        ).view
        await interaction.edit_original_response(content=None, embeds=embeds, view=view)
    except discord.errors.NotFound:
        pass


async def handle_cooldown_error(interaction: discord.Interaction, error: Exception):
    format_values = {'retry_after': round(error.retry_after, 2)}
    embeds = load_embeds('command_cooldown', format_values, color='warning')
    await interaction.response.send_message(embeds=embeds, ephemeral=True)


async def handle_all_errors(interaction: discord.Interaction,
                            client: discord.Client, error: Exception):
    support_url = get_config()["links"]["support_server"]
    try:
        format_values = {'command': interaction.data["name"],
                         'error': error, 'support_url': support_url}
        embeds = load_embeds('errors', format_values, color='danger')
        await interaction.edit_original_response(embeds=embeds)
    except discord.errors.NotFound:
        pass

    # log traceback to discord channel
    await log_error_msg(client, error)
