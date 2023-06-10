import os

import discord
from discord import app_commands
from discord.ext import commands

from render.year import render_year
from helper.functions import (username_autocompletion,
                       session_autocompletion,
                       get_command_cooldown,
                       get_hypixel_data,
                       update_command_stats,
                       authenticate_user,
                       get_smart_session,
                       uuid_to_discord_id,
                       get_subscription,
                       fetch_skin_model,
                       send_generic_renders,
                       get_embed_color,
                       loading_message)


class Year(commands.Cog):
    def __init__(self, client):
        self.client: discord.Client = client
        self.LOADING_MSG = loading_message()


    async def year_command(self, interaction: discord.Interaction,
                           name: str, uuid: str, session: int, year: int):
        refined = name.replace('_', r'\_')

        if session is None: session = 100
        session_data = await get_smart_session(interaction, session, refined, uuid)
        if not session_data: return
        if session == 100: session = session_data[0]

        await interaction.response.send_message(self.LOADING_MSG)
        os.makedirs(f'./database/activerenders/{interaction.id}')
        skin_res = fetch_skin_model(uuid, 144)

        hypixel_data = get_hypixel_data(uuid)

        kwargs = {
            "name": name,
            "uuid": uuid,
            "session": session,
            "year": year,
            "hypixel_data": hypixel_data,
            "skin_res": skin_res,
            "save_dir": interaction.id
        }

        await send_generic_renders(interaction, render_year, kwargs)
        update_command_stats(interaction.user.id, f'year_{year}')


    year_group = app_commands.Group(
        name='year', 
        description='View the a players projected stats for a future year'
    )


    @year_group.command(name = "2024", description = "View the a players projected stats for 2024")
    @app_commands.autocomplete(username=username_autocompletion, session=session_autocompletion)
    @app_commands.describe(username='The player you want to view', session='The session you want to use')
    @app_commands.checks.dynamic_cooldown(get_command_cooldown)
    async def year_2024(self, interaction: discord.Interaction, username: str=None, session: int=None):
        try: name, uuid = await authenticate_user(username, interaction)
        except TypeError: return
        await self.year_command(interaction, name, uuid, session, 2024)


    @year_group.command(name = "2025", description = "View the a players projected stats for 2025")
    @app_commands.autocomplete(username=username_autocompletion, session=session_autocompletion)
    @app_commands.describe(username='The player you want to view', session='The session you want to use')
    @app_commands.checks.dynamic_cooldown(get_command_cooldown)
    async def year_2025(self, interaction: discord.Interaction, username: str=None, session: int=None):
        try: name, uuid = await authenticate_user(username, interaction)
        except TypeError: return

        discord_id = uuid_to_discord_id(uuid)
        subscription = None
        if discord_id:
            subscription = get_subscription(discord_id=discord_id)

        if not subscription and not get_subscription(interaction.user.id):
            embed_color = get_embed_color('primary')
            embed = discord.Embed(
                title="That player doesn't have premium!",
                description='In order to view stats for 2025, a [premium subscription](https://statalytics.net/store) is required!',
                color=embed_color
            )

            embed.add_field(name='How does it work?', value="""
                \- You can view any player's stats for 2025 if you have a premium subscription.
                \- You can view a player's stats for 2025 if they have a premium subscription.
            """.replace('   ', ''))
            await interaction.response.send_message(embed=embed)
            return

        await self.year_command(interaction, name, uuid, session, 2025)


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Year(client))
