import asyncio
from datetime import datetime, timedelta, timezone

import discord
from discord.ext import commands

import helper
import statalib as lib
from statalib import rotational_stats as rotational
from .render import RotationalStatsRenderer


class DailyCommandsCog(commands.Cog):
    @helper.decorators.app_command("daily")
    @helper.interactions.access_permitted_check()
    async def daily(self, interaction: discord.Interaction, player: str | None=None):
        await interaction.response.defer()

        name, uuid = await helper.interactions.fetch_player_info(player, interaction)

        skin_model, hypixel_data = await asyncio.gather(
            lib.network.fetch_skin_model(uuid),
            lib.network.fetch_hypixel_data(uuid)
        )

        manager = rotational.RotationalStatsManager(uuid)
        reset_time = rotational.get_dynamic_reset_time(uuid)

        rotational_data = manager.get_rotational_data(
            rotational.RotationType.from_string('daily'))

        if not rotational_data:
            manager.initialize_rotational_tracking(hypixel_data)

            _ = await interaction.edit_original_response(
                content=f'Historical stats for {lib.fmt.fname(name)} will now be tracked.')
            return

        now = datetime.now(timezone(timedelta(hours=reset_time.utc_offset)))

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

        renderer = RotationalStatsRenderer(
            skin_model,
            name,
            uuid,
            hypixel_data,
            rotational.RotationType.DAILY,
            lib.ModesEnum.OVERALL.value,
        )
        background_img = renderer.bg(interaction.user.id, "daily", uuid)
        img_bytes = await renderer.render_to_buffer(background_img)

        await interaction.followup.send(
            content=message,
            files=[discord.File(img_bytes, filename="overall.png")],
            view=helper.views.FractylModesView(
                interaction_origin=interaction,
                modes=lib.ModesEnum.non_dream_modes(),
                background_img=background_img,
                placeholder="Overall",
                renderer=renderer,
            ).add_item(
                helper.views.info.RotationalResettingInfoButton.button()
            )
        )


    @helper.decorators.app_command("lastday")
    @helper.interactions.access_permitted_check()
    async def lastday(
        self,
        interaction: discord.Interaction,
        player: str | None=None,
        days: int=1
    ):
        await interaction.response.defer()

        name, uuid = await helper.interactions.fetch_player_info(player, interaction)
        discord_id = lib.accounts.uuid_to_discord_id(uuid=uuid)

        max_lookback = rotational.get_max_lookback([discord_id, interaction.user.id])

        if max_lookback is not None and max_lookback < days:
            embed = helper.Embeds.problems.max_lookback_exceeded(max_lookback)
            await interaction.followup.send(embed=embed)
            return

        days = max(days, 1)  # Minimum of 1 day
        reset_time = rotational.get_dynamic_reset_time(uuid)

        now = datetime.now(timezone(timedelta(hours=reset_time.utc_offset)))

        try:
            relative_date = now - timedelta(days=days)

            # today's reset has not occured yet
            if now.hour < reset_time.reset_hour:
                relative_date -= timedelta(days=1)
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
                f'{lib.fmt.fname(name)} has no tracked data for {days} ' +
                f'{lib.fmt.pluralize(days, "day")} ago!')
            return

        skin_model, hypixel_data = await asyncio.gather(
            lib.network.fetch_skin_model(uuid),
            lib.network.fetch_hypixel_data(uuid)
        )

        renderer = RotationalStatsRenderer(
            skin_model,
            name,
            uuid,
            hypixel_data,
            period_id,
            lib.ModesEnum.OVERALL.value,
            periods_ago=days
        )
        background_img = renderer.bg(interaction.user.id, "lastday", uuid)
        img_bytes = await renderer.render_to_buffer(background_img)

        await interaction.followup.send(
            files=[discord.File(img_bytes, filename="overall.png")],
            view=helper.views.FractylModesView(
                interaction_origin=interaction,
                modes=lib.ModesEnum.non_dream_modes(),
                background_img=background_img,
                placeholder="Overall",
                renderer=renderer,
            ).add_item(
                helper.views.info.RotationalResettingInfoButton.button()
            )
        )




async def setup(client: helper.Client) -> None:
    await client.add_cog(DailyCommandsCog())
