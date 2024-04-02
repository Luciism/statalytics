import asyncio
from datetime import datetime, timedelta, timezone

import discord
from discord import app_commands
from discord.ext import commands

import statalib as lib
from render.historical import render_historical


class Daily(commands.Cog):
    def __init__(self, client):
        self.client: commands.Bot = client
        self.LOADING_MSG = lib.loading_message()


    @app_commands.command(
        name="daily",
        description="View the daily stats of a player")
    @app_commands.describe(player='The player you want to view')
    @app_commands.autocomplete(player=lib.username_autocompletion)
    @app_commands.checks.dynamic_cooldown(lib.generic_command_cooldown)
    async def daily(self, interaction: discord.Interaction, player: str=None):
        await interaction.response.defer()
        await lib.run_interaction_checks(interaction)

        name, uuid = await lib.fetch_player_info(player, interaction)

        await interaction.followup.send(self.LOADING_MSG)

        skin_model, hypixel_data = await asyncio.gather(
            lib.fetch_skin_model(uuid, 144),
            lib.fetch_hypixel_data(uuid)
        )

        historic = lib.HistoricalManager(interaction.user.id, uuid)
        gmt_offset, hour = historic.get_reset_time()

        historical_data = historic.get_tracker_data(tracker='daily')

        if not historical_data:
            await historic.start_trackers(hypixel_data)
            await interaction.edit_original_response(
                content=f'Historical stats for {lib.fname(name)} will now be tracked.')
            return

        now = datetime.now(timezone(timedelta(hours=gmt_offset)))
        formatted_date = now.strftime(f"%b {now.day}{lib.ordinal(now.day)}, %Y")

        kwargs = {
            "name": name,
            "uuid": uuid,
            "identifier": "daily",
            "relative_date": formatted_date,
            "title": "Daily Stats",
            "hypixel_data": hypixel_data,
            "skin_model": skin_model,
            "save_dir": interaction.id
        }

        if lib.has_auto_reset(uuid):
            # i dont know why this works but it does so dont touch it
            # it doesnt do what i think it does
            next_occurrence = now.replace(hour=hour, minute=0, second=0, microsecond=0)
            if now >= next_occurrence:
                next_occurrence += timedelta(days=1)
            utc_next_occurrence = next_occurrence.astimezone(timezone.utc)
            timestamp = int(utc_next_occurrence.timestamp())

            message = f':alarm_clock: Resets <t:{timestamp}:R>'
        else:
            # i hate timezones so much
            timestamp = int(lib.timezone_relative_timestamp(historical_data[2]))
            message = f':alarm_clock: Last reset <t:{timestamp}:R>'

        await lib.handle_modes_renders(
            interaction=interaction,
            func=render_historical,
            kwargs=kwargs,
            message=message,
            custom_view=lib.tracker_view()
        )
        lib.update_command_stats(interaction.user.id, 'daily')


    @app_commands.command(
        name="lastday",
        description="View yesterdays stats of a player")
    @app_commands.describe(
        player='The player you want to view',
        days='The lookback amount in days')
    @app_commands.autocomplete(player=lib.username_autocompletion)
    @app_commands.checks.dynamic_cooldown(lib.generic_command_cooldown)
    async def lastday(self, interaction: discord.Interaction,
                      player: str=None, days: int=1):
        await interaction.response.defer()
        await lib.run_interaction_checks(interaction)

        name, uuid = await lib.fetch_player_info(player, interaction)

        historic = lib.HistoricalManager(interaction.user.id, uuid)
        discord_id = lib.uuid_to_discord_id(uuid=uuid)

        max_lookback = historic.get_max_lookback(discord_id, interaction.user.id)

        if -1 != max_lookback < days:
            embeds = historic.build_invalid_lookback_embeds(max_lookback)
            await interaction.followup.send(embeds=embeds)
            return

        days = max(days, 1)
        gmt_offset, reset_hour = historic.get_reset_time()
        now = datetime.now(timezone(timedelta(hours=gmt_offset)))

        try:
            relative_date = now - timedelta(days=days)

            # today's reset has not occured yet
            if now.hour < reset_hour:
                relative_date -= timedelta(days=1)

            formatted_date = relative_date.strftime(
                f"%b {relative_date.day}{lib.ordinal(relative_date.day)}, %Y")

            period = relative_date.strftime("daily_%Y_%m_%d")
        except OverflowError:
            await interaction.followup.send('Big, big number... too big number...')
            return

        historical_data = historic.get_historical_data(period=period)

        if not historical_data:
            await interaction.followup.send(
                f'{lib.fname(name)} has no tracked data for {days} day(s) ago!')
            return

        await interaction.followup.send(self.LOADING_MSG)

        skin_model, hypixel_data = await asyncio.gather(
            lib.fetch_skin_model(uuid, 144),
            lib.fetch_hypixel_data(uuid)
        )

        kwargs = {
            "name": name,
            "uuid": uuid,
            "identifier": "lastday",
            "relative_date": formatted_date,
            "title": f"{days} {lib.pluralize(days, 'Day')} Ago",
            "period": period,
            "hypixel_data": hypixel_data,
            "skin_model": skin_model,
            "save_dir": interaction.id
        }

        await lib.handle_modes_renders(interaction, render_historical, kwargs)
        lib.update_command_stats(interaction.user.id, 'lastday')


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Daily(client))
