import asyncio
from datetime import datetime, timedelta, timezone
from dateutil.relativedelta import relativedelta

import discord
from discord import app_commands
from discord.ext import commands

import statalib as lib
from statalib import rotational_stats as rotational
from render.rotational import render_rotational


class Yearly(commands.Cog):
    def __init__(self, client):
        self.client: commands.Bot = client
        self.LOADING_MSG = lib.loading_message()


    @app_commands.command(
        name="yearly",
        description="View the yearly stats of a player")
    @app_commands.describe(player='The player you want to view')
    @app_commands.autocomplete(player=lib.username_autocompletion)
    @app_commands.checks.dynamic_cooldown(lib.generic_command_cooldown)
    async def yearly(self, interaction: discord.Interaction, player: str=None):
        await interaction.response.defer()
        await lib.run_interaction_checks(interaction)

        name, uuid = await lib.fetch_player_info(player, interaction)

        await interaction.followup.send(self.LOADING_MSG)

        skin_model, hypixel_data = await asyncio.gather(
            lib.fetch_skin_model(uuid, 144),
            lib.fetch_hypixel_data(uuid)
        )

        manager = rotational.RotationalStatsManager(uuid)
        reset_time = rotational.get_dynamic_reset_time(uuid)

        rotational_data = manager.get_rotational_data(
            rotational.RotationType.from_string('yearly'))

        if not rotational_data:
            manager.initialize_rotational_tracking(hypixel_data)

            await interaction.edit_original_response(
                content=f'Historical stats for {lib.fname(name)} will now be tracked.')
            return

        now = datetime.now(timezone(timedelta(hours=reset_time.utc_offset)))
        relative_date = now.strftime(f"%b {now.day}{lib.ordinal(now.day)}, %Y")

        if reset_time.reset_hour > 0:
            reset_time.reset_hour -= 1  # Idk

        if lib.has_auto_reset(uuid):
            next_occurrence = datetime(
                year=now.year+1, month=1, day=1, hour=reset_time.reset_hour, minute=0,
                second=0, tzinfo=timezone(timedelta(hours=reset_time.utc_offset))
            )
            utc_next_occurrence = next_occurrence.astimezone(timezone.utc)
            timestamp = int(utc_next_occurrence.timestamp())

            message = f':alarm_clock: Resets <t:{timestamp}:R>'
        else:
            timestamp = int(
                lib.timezone_relative_timestamp(rotational_data.last_reset_timestamp))
            message = f':alarm_clock: Last reset <t:{timestamp}:R>'

        kwargs = {
            "name": name,
            "uuid": uuid,
            "tracker": "yearly",
            "relative_date": relative_date,
            "title": "Yearly Stats",
            "hypixel_data": hypixel_data,
            "skin_model": skin_model,
            "save_dir": interaction.id
        }

        await lib.handle_modes_renders(
            interaction=interaction,
            func=render_rotational,
            kwargs=kwargs,
            message=message,
            custom_view=lib.tracker_view()
        )

        lib.update_command_stats(interaction.user.id, 'yearly')


    @app_commands.command(
        name="lastyear",
        description="View last years stats of a player")
    @app_commands.describe(
        player='The player you want to view',
        years='The lookback amount in years')
    @app_commands.autocomplete(player=lib.username_autocompletion)
    @app_commands.checks.dynamic_cooldown(lib.generic_command_cooldown)
    async def lastyear(self, interaction: discord.Interaction,
                       player: str=None, years: int=1):
        await interaction.response.defer()
        await lib.run_interaction_checks(interaction)

        name, uuid = await lib.fetch_player_info(player, interaction)
        discord_id = lib.uuid_to_discord_id(uuid=uuid)

        years = max(years, 1)  # Minimum of 1 year

        # Check if user is within their lookback limitations
        # First checks if a user is checking only 1 year back
        # and then checks if the max lookback days are within the given amount
        max_lookback = rotational.get_max_lookback([discord_id, interaction.user.id])

        if years != 1 and max_lookback is not None and max_lookback < (years * 365):
            embeds = rotational.build_invalid_lookback_embeds(max_lookback)
            await interaction.followup.send(embeds=embeds)
            return

        # Get time / date information
        reset_time = rotational.get_dynamic_reset_time(uuid)

        now = datetime.now(timezone(timedelta(hours=reset_time.reset_hour)))
        try:
            relative_date = now - relativedelta(years=years)

            # today's reset has not occured yet
            if now.hour < reset_time.reset_hour:
                relative_date -= timedelta(days=1)

            formatted_date = relative_date.strftime("Year %Y")
        except ValueError:
            await interaction.followup.send('Big, big number... too big number...')
            return

        period_id = rotational.HistoricalRotationPeriodID(
            rotation_type=rotational.RotationType.YEARLY,
            datetime_info=relative_date
        )

        # Check if historical data exists
        manager = rotational.RotationalStatsManager(uuid)
        historical_data = manager.get_historical_rotation_data(period_id.to_string())

        if not historical_data:
            await interaction.followup.send(
                f'{lib.fname(name)} has no tracked data for {years} '
                f'{lib.pluralize(years, "year")} ago!')
            return

        # Render and send
        await interaction.followup.send(self.LOADING_MSG)

        skin_model, hypixel_data = await asyncio.gather(
            lib.fetch_skin_model(uuid, 144),
            lib.fetch_hypixel_data(uuid)
        )

        kwargs = {
            "name": name,
            "uuid": uuid,
            "tracker": "lastyear",
            "relative_date": formatted_date,
            "title": f"{years} {lib.pluralize(years, 'Year')} Ago",
            "hypixel_data": hypixel_data,
            "skin_model": skin_model,
            "save_dir": interaction.id,
            "period_id": period_id
        }

        await lib.handle_modes_renders(interaction, render_rotational, kwargs)
        lib.update_command_stats(interaction.user.id, 'lastyear')


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Yearly(client))
