import sqlite3
from json import load as load_json

import discord
from discord import app_commands
from discord.ext import commands

from helper.functions import update_command_stats, get_embed_color


class Usage(commands.Cog):
    def __init__(self, client):
        self.client: discord.Client = client


    @app_commands.command(name="usage", description="View Command Usage")
    async def usage_stats(self, interaction: discord.Interaction):
        await interaction.response.defer()
        with open('./assets/command_map.json', 'r') as datafile:
            command_map: dict = load_json(datafile)['commands']

        with sqlite3.connect('./database/command_usage.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [table[0] for table in cursor.fetchall()]

            cursor.execute(f'SELECT * FROM overall WHERE discord_id = {interaction.user.id}')
            table_data = cursor.fetchone()
            if not table_data: table_data = (0, 0)
            overall = f'**Overall - {table_data[1]}**'
            description = []

            usage_values = {}
            for table in tables:
                cursor.execute(f'SELECT * FROM {table} WHERE discord_id = {interaction.user.id}')
                table_data = cursor.fetchone()
                if not table_data or table == "overall": continue
                usage_values[command_map.get(table)] = table_data[1]

        for key, value in sorted(usage_values.items(), key=lambda x: x[1], reverse=True):
            description.append(f'`{key}` - `{value}`')

        embed_color = get_embed_color('primary')
        embed = discord.Embed(title="Your Command Usage", description=overall, color=embed_color)
        for i in range(0, len(description), 10):
            sublist = description[i:i+10]
            embed.add_field(name='', value='\n'.join(sublist))
        await interaction.followup.send(embed=embed)

        update_command_stats(interaction.user.id, 'usage')


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Usage(client))
