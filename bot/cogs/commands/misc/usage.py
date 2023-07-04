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
        discord_id = interaction.user.id
        await interaction.response.defer()
        with open('./assets/command_map.json', 'r') as datafile:
            command_map: dict = load_json(datafile)['commands']

        with sqlite3.connect('./database/core.db') as conn:
            cursor = conn.cursor()

            cursor.execute(f"SELECT * FROM command_usage WHERE discord_id = {discord_id}")
            command_usage = cursor.fetchone()

            column_names = [desc[0] for desc in cursor.description]


        usage_dict = {}
        
        if not command_usage:
            embed = discord.Embed(
                title='No Command Usage!',
                description='You have no command usage stats as you have never run a command.',
                color=get_embed_color('primary')
            )
        else:
            for i, usage in enumerate(command_usage[1:]):
                if usage:
                    usage_dict[column_names[i+1]] = usage

            overall = '**Overall - 0**'
            description = []

            for key, value in sorted(usage_dict.items(), key=lambda x: x[1], reverse=True):
                if key == 'overall':
                    overall = f'**Overall - {value}**'
                    continue
                command = command_map.get(key, '/unknown')
                description.append(f'`{command}` - `{value}`')

            embed = discord.Embed(
                title="Your Command Usage",
                description=overall,
                color=get_embed_color('primary')
            )

            for i in range(0, len(description), 10):
                sublist = description[i:i+10]
                embed.add_field(name='', value='\n'.join(sublist))

        await interaction.followup.send(embed=embed)

        update_command_stats(discord_id, 'usage')


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Usage(client))
