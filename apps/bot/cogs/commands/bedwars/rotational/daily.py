import asyncio
from datetime import datetime, timedelta, timezone

import discord
from discord import app_commands
from discord.ext import commands

import helper
import statalib as lib
from statalib import rotational_stats as rotational
from render.rotational import render_rotational


class Daily(commands.Cog):
    def __init__(self, client):
        self.client: commands.Bot = client
        self.LOADING_MSG = lib.loading_message()


    @app_commands.command(
        name="daily",
        description="View the daily stats of a player")
    @app_commands.describe(player='The player you want to view')
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.autocomplete(player=helper.username_autocompletion)
    @app_commands.checks.dynamic_cooldown(helper.generic_command_cooldown)
    async def daily(self, interaction: discord.Interaction, player: str=None):
        await interaction.response.defer()
        await helper.interactions.run_interaction_checks(interaction)

        name, uuid = await helper.interactions.fetch_player_info(player, interaction)

        await interaction.followup.send(self.LOADING_MSG)

        skin_model, hypixel_data = await asyncio.gather(
            lib.network.fetch_skin_model(uuid, 144),
            lib.network.fetch_hypixel_data(uuid)
        )

        manager = rotational.RotationalStatsManager(uuid)
        reset_time = rotational.get_dynamic_reset_time(uuid)

        rotational_data = manager.get_rotational_data(
            rotational.RotationType.from_string('daily'))

        if not rotational_data:
            manager.initialize_rotational_tracking(hypixel_data)

            await interaction.edit_original_response(
                content=f'Historical stats for {lib.fname(name)} will now be tracked.')
            return

        now = datetime.now(timezone(timedelta(hours=reset_time.utc_offset)))
        formatted_date = now.strftime(f"%b {now.day}{lib.ordinal(now.day)}, %Y")

        kwargs = {
            "name": name,
            "uuid": uuid,
            "tracker": "daily",
            "relative_date": formatted_date,
            "title": "Daily Stats",
            "hypixel_data": hypixel_data,
            "skin_model": skin_model,
            "save_dir": interaction.id
        }

        if lib.rotational_stats.has_auto_reset_access(uuid):
            # i dont know why this works but it does so dont touch it
            # it doesnt do what i think it does
            next_occurrence = now.replace(
                hour=reset_time.reset_hour, minute=reset_time.reset_minute,
                second=0, microsecond=0)

            if now >= next_occurrence:
                next_occurrence += timedelta(days=1)

            utc_next_occurrence = next_occurrence.astimezone(timezone.utc)
            timestamp = int(utc_next_occurrence.timestamp())

            message = f':alarm_clock: Resets <t:{timestamp}:R>'
        else:
            # i hate timezones so much
            timestamp = int(
                lib.timezone_relative_timestamp(rotational_data.last_reset_timestamp))
            message = f':alarm_clock: Last reset <t:{timestamp}:R>'

        await helper.interactions.handle_modes_renders(
            interaction=interaction,
            func=render_rotational,
            kwargs=kwargs,
            message=message,
            custom_view=helper.views.tracker_view()
        )
        lib.usage.update_command_stats(interaction.user.id, 'daily')


    @app_commands.command(
        name="lastday",
        description="View yesterdays stats of a player")
    @app_commands.describe(
        player='The player you want to view',
        days='The lookback amount in days')
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.autocomplete(player=helper.username_autocompletion)
    @app_commands.checks.dynamic_cooldown(helper.generic_command_cooldown)
    async def lastday(self, interaction: discord.Interaction,
                      player: str=None, days: int=1):
        await interaction.response.defer()
        await helper.interactions.run_interaction_checks(interaction)

        name, uuid = await helper.interactions.fetch_player_info(player, interaction)
        discord_id = lib.accounts.uuid_to_discord_id(uuid=uuid)

        max_lookback = rotational.get_max_lookback([discord_id, interaction.user.id])

        if max_lookback is not None and max_lookback < days:
            embeds = rotational.build_invalid_lookback_embeds(max_lookback)
            await interaction.followup.send(embeds=embeds)
            return

        days = max(days, 1)  # Minimum of 1 day
        reset_time = rotational.get_dynamic_reset_time(uuid)

        now = datetime.now(timezone(timedelta(hours=reset_time.utc_offset)))

        try:
            relative_date = now - timedelta(days=days)

            # today's reset has not occured yet
            if now.hour < reset_time.reset_hour:
                relative_date -= timedelta(days=1)

            formatted_date = relative_date.strftime(
                f"%b {relative_date.day}{lib.ordinal(relative_date.day)}, %Y")
        except OverflowError:
            await interaction.followup.send('Big, big number... too big number...')
            return

        period_id = rotational.HistoricalRotationPeriodID(
            rotation_type=rotational.RotationType.DAILY,
            datetime_info=relative_date
        )

        manager = rotational.RotationalStatsManager(uuid)
        historical_data = manager.get_historical_rotation_data(period_id.to_string())

        if not historical_data:
            await interaction.followup.send(
                f'{lib.fname(name)} has no tracked data for {days} '
                f'{lib.pluralize(days, "day")} ago!')
            return

        await interaction.followup.send(self.LOADING_MSG)

        skin_model, hypixel_data = await asyncio.gather(
            lib.network.fetch_skin_model(uuid, 144),
            lib.network.fetch_hypixel_data(uuid)
        )

        kwargs = {
            "name": name,
            "uuid": uuid,
            "tracker": "lastday",
            "relative_date": formatted_date,
            "title": f"{days} {lib.pluralize(days, 'Day')} Ago",
            "hypixel_data": hypixel_data,
            "skin_model": skin_model,
            "save_dir": interaction.id,
            "period_id": period_id
        }

        await helper.interactions.handle_modes_renders(interaction, render_rotational, kwargs)
        lib.usage.update_command_stats(interaction.user.id, 'lastday')


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Daily(client))
