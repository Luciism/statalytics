import sqlite3
from json import load as load_json

import discord
from discord import app_commands
from discord.ext import commands

import statalib as lib
import helper


class Usage(commands.Cog):
    def __init__(self, client):
        self.client: commands.Bot = client


    @app_commands.command(name="usage", description="View Command Usage")
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    async def usage_stats(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await helper.interactions.run_interaction_checks(interaction)

        discord_id = interaction.user.id

        with sqlite3.connect(f'{lib.REL_PATH}/database/core.db') as conn:
            cursor = conn.cursor()

            cursor.execute(
                f"SELECT * FROM command_usage WHERE discord_id = {discord_id}")
            command_usage = cursor.fetchone()

            column_names = [desc[0] for desc in cursor.description]


        usage_dict = {}

        if not command_usage:
            embed = discord.Embed(
                title='No Command Usage!',
                description='You have no command usage stats'
                            'as you have never run a command.',
                color=lib.get_embed_color('primary')
            )
        else:
            for i, usage in enumerate(command_usage[1:]):
                if usage:
                    usage_dict[column_names[i+1]] = usage

            overall = '**Overall - 0**'
            description = []

            sorted_usage = sorted(
                usage_dict.items(),
                key=lambda x: x[1],
                reverse=True
            )

            for key, value in sorted_usage:
                if key == 'overall':
                    overall = f'**Overall - {value}**'
                    continue
                command = lib.ASSET_LOADER.command_map.get(key, '/unknown')
                description.append(f'`{command}` - `{value}`')

            embed = discord.Embed(
                title="Your Command Usage",
                description=overall,
                color=lib.get_embed_color('primary')
            )

            for i in range(0, len(description), 10):
                sublist = description[i:i+10]
                embed.add_field(name='', value='\n'.join(sublist))

        await interaction.followup.send(embed=embed)

        lib.update_command_stats(discord_id, 'usage')


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Usage(client))
