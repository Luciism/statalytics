import os
import sqlite3
from datetime import datetime, timedelta, timezone

import discord
from discord import app_commands
from discord.ext import commands

from render.difference import render_difference
from helper.functions import (username_autocompletion,
                       get_command_cooldown,
                       get_hypixel_data,
                       update_command_stats,
                       authenticate_user,
                       start_historical,
                       uuid_to_discord_id,
                       yearly_eligibility,
                       get_time_config,
                       fetch_skin_model,
                       ordinal,
                       send_generic_renders)


class Difference(commands.Cog):
    def __init__(self, client):
        self.client: discord.Client = client
        self.GENERATING_MESSAGE = 'Generating please wait <a:loading1:1062561739989860462>'

    difference_group = app_commands.Group(
        name='difference', 
        description='View the stat difference of a player over a period of time'
    )


    async def difference_command(self, interaction: discord.Interaction, username: str, method: str):
        try: name, uuid = await authenticate_user(username, interaction)
        except TypeError: return
        refined = name.replace("_", "\_")

        discord_id = uuid_to_discord_id(uuid=uuid)
        if method == 'yearly':
            result = await yearly_eligibility(interaction, discord_id)
            if not result: return

        gmt_offset, _ = get_time_config(discord_id=discord_id)

        with sqlite3.connect('./database/historical.db') as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT uuid FROM {method} WHERE uuid = '{uuid}'")
            historical_data = cursor.fetchone()

        if not historical_data:
            await interaction.response.defer()
            start_historical(uuid=uuid, method=method)
            await interaction.followup.send(f'{method.title()} stats for {refined} will now be tracked.')
            return

        await interaction.response.send_message(self.GENERATING_MESSAGE)
        os.makedirs(f'./database/activerenders/{interaction.id}')
        skin_res = fetch_skin_model(uuid, 144)
        hypixel_data = get_hypixel_data(uuid)

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

        await send_generic_renders(interaction, render_difference, kwargs)
        update_command_stats(interaction.user.id, f'difference_{method}')


    @difference_group.command(name = "daily", description = "View the daily stas difference of a player")
    @app_commands.autocomplete(username=username_autocompletion)
    @app_commands.describe(username='The player you want to view')
    @app_commands.checks.dynamic_cooldown(get_command_cooldown)
    async def daily(self, interaction: discord.Interaction, username: str=None):
        await self.difference_command(interaction, username, 'daily')


    @difference_group.command(name = "weekly", description = "View the weekly stat difference of a player")
    @app_commands.autocomplete(username=username_autocompletion)
    @app_commands.describe(username='The player you want to view')
    @app_commands.checks.dynamic_cooldown(get_command_cooldown)
    async def weekly(self, interaction: discord.Interaction, username: str=None):
        await self.difference_command(interaction, username, 'weekly')


    @difference_group.command(name = "monthly", description = "View the monthly stat difference of a player")
    @app_commands.autocomplete(username=username_autocompletion)
    @app_commands.describe(username='The player you want to view')
    @app_commands.checks.dynamic_cooldown(get_command_cooldown)
    async def monthly(self, interaction: discord.Interaction, username: str=None):
        await self.difference_command(interaction, username, 'monthly')


    @difference_group.command(name = "yearly", description = "View the yearly stat difference of a player")
    @app_commands.autocomplete(username=username_autocompletion)
    @app_commands.describe(username='The player you want to view')
    @app_commands.checks.dynamic_cooldown(get_command_cooldown)
    async def yearly(self, interaction: discord.Interaction, username: str=None):
        await self.difference_command(interaction, username, 'yearly')


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Difference(client))
