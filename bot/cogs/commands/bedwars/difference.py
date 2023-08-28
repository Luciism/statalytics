import asyncio
from datetime import datetime, timedelta, timezone

import discord
from discord import app_commands
from discord.ext import commands

from render.difference import render_difference
from statalib import (
    HistoricalManager,
    fetch_player_info,
    uuid_to_discord_id,
    username_autocompletion,
    generic_command_cooldown,
    fetch_hypixel_data,
    update_command_stats,
    fetch_skin_model,
    ordinal, loading_message,
    handle_modes_renders,
    yearly_eligibility_check,
    fname
)


class Difference(commands.Cog):
    def __init__(self, client):
        self.client: commands.Bot = client
        self.LOADING_MSG = loading_message()


    difference_group = app_commands.Group(
        name='difference',
        description='View the stat difference of a player over a period of time'
    )


    async def difference_command(self, interaction: discord.Interaction,
                                 player: str, method: str):
        await interaction.response.defer()
        name, uuid = await fetch_player_info(player, interaction)

        historic = HistoricalManager(interaction.user.id, uuid)

        discord_id = uuid_to_discord_id(uuid=uuid)
        if method == 'yearly':
            result = await yearly_eligibility_check(interaction, discord_id)
            if not result:
                return

        gmt_offset = historic.get_reset_time()[0]
        historical_data = historic.get_historical(identifier=method)

        if not historical_data:
            await historic.start_historical()
            await interaction.followup.send(
                f'Historical stats for {fname(name)} will now be tracked.')
            return

        await interaction.followup.send(self.LOADING_MSG)

        skin_model, hypixel_data = await asyncio.gather(
            fetch_skin_model(uuid, 144),
            fetch_hypixel_data(uuid)
        )

        now = datetime.now(timezone(timedelta(hours=gmt_offset)))
        formatted_date = now.strftime(f"%b {now.day}{ordinal(now.day)}, %Y")

        kwargs = {
            "name": name,
            "uuid": uuid,
            "relative_date": formatted_date,
            "method": method,
            "hypixel_data": hypixel_data,
            "skin_model": skin_model,
            "save_dir": interaction.id
        }

        await handle_modes_renders(interaction, render_difference, kwargs)
        update_command_stats(interaction.user.id, f'difference_{method}')


    @difference_group.command(
            name="daily",
            description="View the daily stas difference of a player")
    @app_commands.describe(player='The player you want to view')
    @app_commands.autocomplete(player=username_autocompletion)
    @app_commands.checks.dynamic_cooldown(generic_command_cooldown)
    async def daily(self, interaction: discord.Interaction, player: str=None):
        await self.difference_command(interaction, player, 'daily')


    @difference_group.command(
        name="weekly",
        description="View the weekly stat difference of a player")
    @app_commands.describe(player='The player you want to view')
    @app_commands.autocomplete(player=username_autocompletion)
    @app_commands.checks.dynamic_cooldown(generic_command_cooldown)
    async def weekly(self, interaction: discord.Interaction, player: str=None):
        await self.difference_command(interaction, player, 'weekly')


    @difference_group.command(
        name="monthly",
        description="View the monthly stat difference of a player")
    @app_commands.describe(player='The player you want to view')
    @app_commands.autocomplete(player=username_autocompletion)
    @app_commands.checks.dynamic_cooldown(generic_command_cooldown)
    async def monthly(self, interaction: discord.Interaction, player: str=None):
        await self.difference_command(interaction, player, 'monthly')


    @difference_group.command(
        name="yearly",
        description="View the yearly stat difference of a player")
    @app_commands.describe(player='The player you want to view')
    @app_commands.autocomplete(player=username_autocompletion)
    @app_commands.checks.dynamic_cooldown(generic_command_cooldown)
    async def yearly(self, interaction: discord.Interaction, player: str=None):
        await self.difference_command(interaction, player, 'yearly')


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Difference(client))
