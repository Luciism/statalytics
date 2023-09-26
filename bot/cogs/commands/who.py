import discord
from discord import app_commands
from discord.ext import commands

from statalib import (
    update_command_stats,
    fetch_player_info,
    run_interaction_checks
)


class Who(commands.Cog):
    def __init__(self, client):
        self.client: commands.Bot = client


    @app_commands.command(
        name="who",
        description="Convert the name of uuid of a player")
    @app_commands.describe(
        player='The player whos username / uuid you want to view')
    async def who(self, interaction: discord.Interaction,
                  player: str=None):
        await run_interaction_checks(interaction)

        name, uuid = await fetch_player_info(player, interaction, eph=True)

        if player is None or len(player) <= 16:
            await interaction.response.send_message(
                f'UUID for **{name}** -> `{uuid}`', ephemeral=True)
        else:
            await interaction.response.send_message(
                f'Name for **{uuid}** -> `{name}`', ephemeral=True)

        update_command_stats(interaction.user.id, 'who')


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Who(client))
