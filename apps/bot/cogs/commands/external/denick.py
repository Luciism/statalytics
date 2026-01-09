# api.antisniper.net

import os
import asyncio
import discord
from http.client import RemoteDisconnected
from json import JSONDecodeError

from aiohttp import ClientSession, ClientTimeout, ContentTypeError, ClientConnectionError
from discord import app_commands
from discord.ext import commands
from requests import ReadTimeout, ConnectTimeout

import statalib as lib
import helper


class NumberDenickCommandCog(commands.Cog):
    async def fetch_denick_data(self, mode: str, count: int):
        try:
            async with ClientSession() as session:
                res = await session.get(
                    url=f"https://api.antisniper.net/v2/other/denick/number/{mode}?value={count}",
                    headers={"Apikey": os.getenv('API_KEY_ANTISNIPER') or ""},
                    timeout=ClientTimeout(total=10)
                )
                return await res.json()
        except (ReadTimeout, ConnectTimeout, TimeoutError, asyncio.TimeoutError,
                JSONDecodeError, RemoteDisconnected, ContentTypeError, ClientConnectionError):
            return None


    @helper.decorators.app_command("numberdenick")
    @helper.interactions.access_permitted_check()
    @app_commands.choices(mode=[
        app_commands.Choice(name="Finals", value="finals"),
        app_commands.Choice(name="Beds", value="beds")
    ])
    async def numberdenick(
        self,
        interaction: discord.Interaction,
        mode: app_commands.Choice[str],
        count: int
    ):
        await interaction.response.defer()

        if mode.value not in ('finals', 'beds'):
            await interaction.followup.send('Invalid mode! Valid options: (finals / beds)')
            return

        data = await self.fetch_denick_data(mode.value, count)

        if data is None:
            await interaction.followup.send(
                embed=helper.Embeds.problems.antisniper_connection_error())
            return

        embed_color = lib.config.embed_color('primary')
        embed = discord.Embed(
            title='Number Denicker',
            description=
                f'Mode: {mode}\n' +
                f'Count: {count}\n' +
                f'Results: {len(data["data"])}',
            color=embed_color
        ).set_footer(
            text="Powered by antisniper.net",
            icon_url='https://statalytics.net/image/antisniper.png'
        )

        if data['data']:
            usernames: list[str] = []
            for player in data['data']:
                usernames.append(f'**[{player["star"]}✫] {player["ign"]}**')

            final_kills: list[str] = []
            for player in data['data']:
                final_kills.append(f'{player["final_kills"]:,}')

            beds_broken: list[str] = []
            for player in data['data']:
                beds_broken.append(f'{player["beds_broken"]:,}')

            _ = (embed
                .add_field(name='Username', value='\n\n'.join(usernames))
                .add_field(name='Finals', value='\n\n'.join(final_kills))
                .add_field(name='Beds', value='\n\n'.join(beds_broken))
            )
        else:
            embed.description = "No data."

        await interaction.followup.send(embed=embed)


async def setup(client: helper.Client) -> None:
    await client.add_cog(NumberDenickCommandCog(client))
