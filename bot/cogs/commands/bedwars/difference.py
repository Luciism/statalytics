import os
from datetime import datetime, timedelta, timezone

import discord
from discord import app_commands
from discord.ext import commands

from render.difference import render_difference
from helper import (
    HistoricalManager,
    fetch_player_info,
    uuid_to_discord_id,
    username_autocompletion,
    get_command_cooldown,
    get_hypixel_data,
    update_command_stats,
    fetch_skin_model,
    ordinal, loading_message,
    handle_modes_renders,
    yearly_eligibility_check,
    fname
)


class Difference(commands.Cog):
    def __init__(self, client):
        self.client: discord.Client = client
        self.LOADING_MSG = loading_message()


    difference_group = app_commands.Group(
        name='difference',
        description='View the stat difference of a player over a period of time'
    )


    async def difference_command(self, interaction: discord.Interaction, username: str, method: str):
        await interaction.response.defer()
        name, uuid = await fetch_player_info(username, interaction)

        historic = HistoricalManager(interaction.user.id, uuid)

        discord_id = uuid_to_discord_id(uuid=uuid)
        if method == 'yearly':
            result = await yearly_eligibility_check(interaction, discord_id)
            if not result:
                return

        gmt_offset = historic.get_reset_time()[0]
        historical_data = historic.get_historical(table_name=method)

        if not historical_data:
            await historic.start_historical()
            await interaction.followup.send(f'Historical stats for {fname(name)} will now be tracked.')
            return

        await interaction.followup.send(self.LOADING_MSG)
        skin_res = await fetch_skin_model(uuid, 144)
        hypixel_data = await get_hypixel_data(uuid)

        now = datetime.now(timezone(timedelta(hours=gmt_offset)))
        formatted_date = now.strftime(f"%b {now.day}{ordinal(now.day)}, %Y")

        kwargs = {
            "name": name,
            "uuid": uuid,
            "relative_date": formatted_date,
            "method": method,
            "hypixel_data": hypixel_data,
            "skin_res": skin_res,
            "save_dir": interaction.id
        }

        await handle_modes_renders(interaction, render_difference, kwargs)
        update_command_stats(interaction.user.id, f'difference_{method}')


    @difference_group.command(name="daily", description="View the daily stas difference of a player")
    @app_commands.autocomplete(username=username_autocompletion)
    @app_commands.describe(username='The player you want to view')
    @app_commands.checks.dynamic_cooldown(get_command_cooldown)
    async def daily(self, interaction: discord.Interaction, username: str=None):
        await self.difference_command(interaction, username, 'daily')


    @difference_group.command(name="weekly", description="View the weekly stat difference of a player")
    @app_commands.autocomplete(username=username_autocompletion)
    @app_commands.describe(username='The player you want to view')
    @app_commands.checks.dynamic_cooldown(get_command_cooldown)
    async def weekly(self, interaction: discord.Interaction, username: str=None):
        await self.difference_command(interaction, username, 'weekly')


    @difference_group.command(name="monthly", description="View the monthly stat difference of a player")
    @app_commands.autocomplete(username=username_autocompletion)
    @app_commands.describe(username='The player you want to view')
    @app_commands.checks.dynamic_cooldown(get_command_cooldown)
    async def monthly(self, interaction: discord.Interaction, username: str=None):
        await self.difference_command(interaction, username, 'monthly')


    @difference_group.command(name="yearly", description="View the yearly stat difference of a player")
    @app_commands.autocomplete(username=username_autocompletion)
    @app_commands.describe(username='The player you want to view')
    @app_commands.checks.dynamic_cooldown(get_command_cooldown)
    async def yearly(self, interaction: discord.Interaction, username: str=None):
        await self.difference_command(interaction, username, 'yearly')


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Difference(client))
