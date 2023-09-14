import asyncio

import discord
from discord import app_commands
from discord.ext import commands

from render.year import render_year
from statalib import (
    fetch_player_info,
    uuid_to_discord_id,
    username_autocompletion,
    session_autocompletion,
    generic_command_cooldown,
    fetch_hypixel_data,
    update_command_stats,
    find_dynamic_session_interaction,
    get_subscription,
    fetch_skin_model,
    handle_modes_renders,
    loading_message,
    load_embeds
)


class Year(commands.Cog):
    def __init__(self, client):
        self.client: commands.Bot = client
        self.LOADING_MSG = loading_message()


    year_group = app_commands.Group(
        name='year',
        description='View the a players projected stats for a future year'
    )


    async def year_command(self, interaction: discord.Interaction,
                           name: str, uuid: str, session: int, year: int):
        session = await find_dynamic_session_interaction(interaction, name, uuid, session)

        await interaction.followup.send(self.LOADING_MSG)

        skin_model, hypixel_data = await asyncio.gather(
            fetch_skin_model(uuid, 144),
            fetch_hypixel_data(uuid)
        )

        kwargs = {
            "name": name,
            "uuid": uuid,
            "session": session,
            "year": year,
            "hypixel_data": hypixel_data,
            "skin_model": skin_model,
            "save_dir": interaction.id
        }

        await handle_modes_renders(interaction, render_year, kwargs)
        update_command_stats(interaction.user.id, f'year_{year}')


    @year_group.command(
        name="2024",
        description="View the a players projected stats for 2024")
    @app_commands.describe(
        player='The player you want to view',
        session='The session you want to use')
    @app_commands.autocomplete(
        player=username_autocompletion,
        session=session_autocompletion)
    @app_commands.checks.dynamic_cooldown(generic_command_cooldown)
    async def year_2024(self, interaction: discord.Interaction,
                        player: str=None, session: int=None):
        await interaction.response.defer()
        name, uuid = await fetch_player_info(player, interaction)
        await self.year_command(interaction, name, uuid, session, 2024)


    @year_group.command(
        name="2025",
        description="View the a players projected stats for 2025")
    @app_commands.describe(
        player='The player you want to view',
        session='The session you want to use')
    @app_commands.autocomplete(
        player=username_autocompletion,
        session=session_autocompletion)
    @app_commands.checks.dynamic_cooldown(generic_command_cooldown)
    async def year_2025(self, interaction: discord.Interaction,
                        player: str=None, session: int=None):
        await interaction.response.defer()
        name, uuid = await fetch_player_info(player, interaction)

        discord_id = uuid_to_discord_id(uuid)
        subscription = None
        if discord_id:
            subscription = get_subscription(discord_id=discord_id)

        if not subscription and not get_subscription(interaction.user.id):
            embeds = load_embeds('2025', color='primary')
            await interaction.followup.send(embeds=embeds)
            return

        await self.year_command(interaction, name, uuid, session, 2025)


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Year(client))
