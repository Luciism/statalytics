import sqlite3

import discord
from discord import app_commands
from discord.ext import commands

from statalib import (
    linking_interaction,
    update_command_stats,
    generic_command_cooldown
)


class Linking(commands.Cog):
    def __init__(self, client):
        self.client: discord.Client = client


    @app_commands.command(name="link", description="Link your account")
    @app_commands.checks.dynamic_cooldown(generic_command_cooldown)
    @app_commands.describe(username='The player you want to link to')
    async def link(self, interaction: discord.Interaction, username: str):
        await linking_interaction(interaction, username)
        update_command_stats(interaction.user.id, 'link')


    @app_commands.command(name="unlink", description="Unlink your account")
    async def unlink(self, interaction: discord.Interaction):
        await interaction.response.defer()

        with sqlite3.connect('./database/core.db') as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM linked_accounts WHERE discord_id = ?",
                (interaction.user.id,))

            if cursor.fetchone():
                cursor.execute(
                    "DELETE FROM linked_accounts WHERE discord_id = ?",
                    (interaction.user.id,))
                message = 'Successfully unlinked your account!'
            else:
                message = "You don't have an account linked! In order to link use `/link`!"

        await interaction.followup.send(message)
        update_command_stats(interaction.user.id, 'unlink')


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Linking(client))
