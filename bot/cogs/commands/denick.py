import json
import random
import typing
import requests
import discord

from discord import app_commands
from discord.ext import commands

from helper.functions import (
    get_command_cooldown,
    update_command_stats,
    get_embed_color,
    to_thread
)


class Denick(commands.Cog):
    def __init__(self, client):
        self.client: discord.Client = client


    async def number_autocomplete(self, interaction: discord.Interaction,
                                  current: str) -> typing.List[app_commands.Choice[str]]:
        data = [
            app_commands.Choice(name="finals", value="finals"),
            app_commands.Choice(name="beds", value="beds")
        ]
        return data


    @to_thread
    def fetch_denick_data(self, mode, count):
        with open('./database/apikeys.json', 'r') as datafile:
            all_keys: dict = json.load(datafile)['antisniper']
            key = all_keys[random.choice(list(all_keys.keys()))]

        res = requests.get(f'https://api.antisniper.net/v2/other/denick/number/{mode}?key={key}&value={count}')
        return res.json()


    @app_commands.command(name="numberdenick", description="Find the ign of a nick based on their kill messages (powered by antisniper)")
    @app_commands.describe(mode='The stat to denick with (finals / beds)', count='The count of the chosen stat')
    @app_commands.autocomplete(mode=number_autocomplete)
    @app_commands.checks.dynamic_cooldown(get_command_cooldown)
    async def numberdenick(self, interaction: discord.Interaction, mode: str, count: int):
        await interaction.response.defer()
        mode = mode.lower()
        if not mode in ('finals', 'beds'):
            await interaction.followup.send('Invalid mode! Valid options: (finals / beds)')
            return

        data = await self.fetch_denick_data(mode, count)

        embed_color = get_embed_color(embed_type='primary')
        embed = discord.Embed(
            title='Number Denicker',
            description=f'Mode: {mode}\nCount: {count}\nResults: {len(data["data"])}', color=embed_color
        )

        if data['data']:
            usernames = []
            for player in data['data']:
                usernames.append(f'**[{player["star"]}✫] {player["ign"]}**')

            final_kills = []
            for player in data['data']:
                final_kills.append(f'{player["final_kills"]:,}')

            beds_broken = []
            for player in data['data']:
                beds_broken.append(f'{player["beds_broken"]:,}')

            embed.add_field(name='Username', value='\n\n'.join(usernames))
            embed.add_field(name='Finals', value='\n\n'.join(final_kills))
            embed.add_field(name='Beds', value='\n\n'.join(beds_broken))
        else:
            embed.description = "No data."
        embed.set_footer(text="Powered by antisniper.net", icon_url='https://statalytics.net/image/antisniper.png')
        await interaction.followup.send(embed=embed)
        
        update_command_stats(interaction.user.id, 'numberdenick')


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Denick(client))
