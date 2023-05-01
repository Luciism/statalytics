import json
import sqlite3

import discord
from discord import app_commands
from discord.ext import commands

from ui import SubmitSuggestion
from functions import update_command_stats


class Misc(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.GENERATING_MESSAGE = 'Generating please wait <a:loading1:1062561739989860462>'

    # Help command
    @app_commands.command(name = "help", description = "Help Page")
    async def get_help(self, interaction: discord.Interaction):
        with open('./assets/help.json', 'r') as datafile:
            embed_data = json.load(datafile)

        embeds = [discord.Embed.from_dict(embed) for embed in embed_data['embeds']]
        await interaction.response.send_message(embeds=embeds, ephemeral=True)

        update_command_stats(interaction.user.id, 'help')

    # Invite
    @app_commands.command(name='invite', description=f'Invite Statalytics to your server')
    async def invite(self, interaction: discord.Interaction):
        await interaction.response.send_message(f'To add Statalytics to your server, click [here](https://discord.com/api/oauth2/authorize?client_id=903765373181112360&permissions=414464724033&scope=bot)')

    # Suggest
    @app_commands.command(name='suggest', description='Suggest a feature you would like to see added!')
    async def suggest(self, interaction: discord.Interaction):
        channel = self.client.get_channel(1065918528236040232)
        await interaction.response.send_modal(SubmitSuggestion(channel))

    # Usage command
    @app_commands.command(name = "usage", description = "View Command Usage")
    async def usage_stats(self, interaction: discord.Interaction):
        with open('./assets/command_map.json', 'r') as datafile:
            command_map = json.load(datafile)['commands']

        with sqlite3.connect('./database/command_usage.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [table[0] for table in cursor.fetchall()]

            cursor.execute(f'SELECT * FROM overall WHERE discord_id = {interaction.user.id}')
            table_data = cursor.fetchone()
            if not table_data: table_data = (0, 0)
            description = [f'**Overall - {table_data[1]}**\n\n']

            for table in tables:
                cursor.execute(f'SELECT * FROM {table} WHERE discord_id = {interaction.user.id}')
                table_data = cursor.fetchone()
                if not table_data: table_data = (0, 0)
                if table != "overall":
                    description.append(f'`{command_map.get(table)}` - `{table_data[1]}`\n')

        embed = discord.Embed(title="Your Command Usage", description=''.join(description), color=0x5865F2)
        await interaction.response.send_message(embed=embed)


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Misc(client))
