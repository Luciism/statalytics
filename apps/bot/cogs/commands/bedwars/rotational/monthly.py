import asyncio
from datetime import datetime, timedelta, timezone
from dateutil.relativedelta import relativedelta

import discord
from discord import app_commands
from discord.ext import commands

import helper
import statalib as lib
from statalib import rotational_stats as rotational
from render.rotational import render_rotational


class Monthly(commands.Cog):
    def __init__(self, client):
        self.client: commands.Bot = client
        self.LOADING_MSG = lib.loading_message()


    @app_commands.command(
        name="monthly",
        description="View the monthly stats of a player")
    @app_commands.describe(player='The player you want to view')
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.autocomplete(player=lib.username_autocompletion)
    @app_commands.checks.dynamic_cooldown(helper.generic_command_cooldown)
    async def monthly(self, interaction: discord.Interaction, player: str=None):
        await interaction.response.defer()
        await helper.interactions.run_interaction_checks(interaction)

        name, uuid = await helper.interactions.fetch_player_info(player, interaction)

        await interaction.followup.send(self.LOADING_MSG)

        skin_model, hypixel_data = await asyncio.gather(
            lib.fetch_skin_model(uuid, 144),
            lib.fetch_hypixel_data(uuid)
        )

        manager = rotational.RotationalStatsManager(uuid)
        reset_time = rotational.get_dynamic_reset_time(uuid)

        rotational_data = manager.get_rotational_data(
            rotational.RotationType.from_string('monthly'))

        if not rotational_data:
            manager.initialize_rotational_tracking(hypixel_data)

            await interaction.edit_original_response(
                content=f'Historical stats for {lib.fname(name)} will now be tracked.')
            return

        now = datetime.now(timezone(timedelta(hours=reset_time.utc_offset)))
        formatted_date = now.strftime(f"%b {now.day}{lib.ordinal(now.day)}, %Y")


        if lib.rotational_stats.has_auto_reset_access(uuid):
            next_occurrence = now.replace(
                hour=reset_time.reset_hour, minute=0, second=0, microsecond=0)

            if now >= next_occurrence:
                next_month = next_occurrence.month + 1

                if next_month > 12:
                    # wrap to the next year
                    next_year = next_occurrence.year + next_month // 12
                    next_month = next_month % 12

                    next_occurrence = next_occurrence.replace(
                        day=1, month=next_month, year=next_year)
                else:
                    next_occurrence = next_occurrence.replace(day=1, month=next_month)

            while next_occurrence.day != 1:
                next_occurrence += timedelta(days=1)
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
            "tracker": "monthly",
            "relative_date": formatted_date,
            "title": "Monthly Stats",
            "hypixel_data": hypixel_data,
            "skin_model": skin_model,
            "save_dir": interaction.id
        }

        await helper.interactions.handle_modes_renders(
            interaction=interaction,
            func=render_rotational,
            kwargs=kwargs,
            message=message,
            custom_view=helper.views.tracker_view()
        )
        lib.update_command_stats(interaction.user.id, 'monthly')


    @app_commands.command(
        name="lastmonth",
        description="View last months stats of a player")
    @app_commands.describe(
        player='The player you want to view',
        months='The lookback amount in months')
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.autocomplete(player=lib.username_autocompletion)
    @app_commands.checks.dynamic_cooldown(helper.generic_command_cooldown)
    async def lastmonth(self, interaction: discord.Interaction,
                        player: str=None, months: int=1):
        await interaction.response.defer()
        await helper.interactions.run_interaction_checks(interaction)

        name, uuid = await helper.interactions.fetch_player_info(player, interaction)
        discord_id = lib.uuid_to_discord_id(uuid=uuid)

        max_lookback = rotational.get_max_lookback([discord_id, interaction.user.id])

        if max_lookback is not None and max_lookback < (months * 30):
            embeds = rotational.build_invalid_lookback_embeds(max_lookback)
            await interaction.followup.send(embeds=embeds)
            return

        months = max(months, 1)  # Minimum of 1 month
        reset_time = rotational.get_dynamic_reset_time(uuid)

        now = datetime.now(timezone(timedelta(hours=reset_time.utc_offset)))

        try:
            relative_date = now - relativedelta(months=months)

            # today's reset has not occured yet
            if now.hour < reset_time.reset_hour:
                relative_date -= timedelta(days=1)

            formatted_date = relative_date.strftime("%b %Y")
        except ValueError:
            await interaction.followup.send('Big, big number... too big number...')
            return

        period_id = rotational.HistoricalRotationPeriodID(
            rotation_type=rotational.RotationType.MONTHLY,
            datetime_info=relative_date
        )

        manager = rotational.RotationalStatsManager(uuid)
        historical_data = manager.get_historical_rotation_data(period_id.to_string())

        if not historical_data:
            await interaction.followup.send(
                f'{lib.fname(name)} has no tracked data for {months} '
                f'{lib.pluralize(months, "month")} ago!')
            return

        await interaction.followup.send(self.LOADING_MSG)

        skin_model, hypixel_data = await asyncio.gather(
            lib.fetch_skin_model(uuid, 144),
            lib.fetch_hypixel_data(uuid)
        )

        kwargs = {
            "name": name,
            "uuid": uuid,
            "tracker": "lastmonth",
            "relative_date": formatted_date,
            "title": f"{months} {lib.pluralize(months, 'Month')} Ago",
            "hypixel_data": hypixel_data,
            "skin_model": skin_model,
            "save_dir": interaction.id,
            "period_id": period_id
        }

        await helper.interactions.handle_modes_renders(interaction, render_rotational, kwargs)
        lib.update_command_stats(interaction.user.id, 'lastmonth')


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Monthly(client))
