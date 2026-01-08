import asyncio
from datetime import datetime, timedelta, timezone

import discord
from discord import app_commands
from discord.ext import commands

import helper
import statalib as lib
from statalib import rotational_stats as rotational
from render.difference import render_difference


class DifferenceCommandCog(commands.Cog):
    difference_group: app_commands.Group = app_commands.Group(
        name='difference',
        description='View the stat difference of a player over a period of time',
        allowed_contexts=app_commands.AppCommandContext(
            guild=True, dm_channel=True, private_channel=True),
        allowed_installs=app_commands.AppInstallationType(guild=True, user=True)
    )


    async def difference_command(
        self, interaction: discord.Interaction, player: str, tracker: str
    ) -> None:
        await interaction.response.defer()

        name, uuid = await helper.interactions.fetch_player_info(player, interaction)

        await interaction.followup.send(lib.config.loading_message())

        skin_model, hypixel_data = await asyncio.gather(
            lib.network.fetch_skin_model(uuid, 144),
            lib.network.fetch_hypixel_data(uuid)
        )

        utc_offset = rotational.get_dynamic_reset_time(uuid).utc_offset
        manager = rotational.RotationalStatsManager(uuid)

        rotational_data = manager.get_rotational_data(
            rotational.RotationType.from_string(tracker))

        if not rotational_data:
            manager.initialize_rotational_tracking(hypixel_data)

            _ = await interaction.edit_original_response(
                content=f'Historical stats for {lib.fmt.fname(name)} will now be tracked.')
            return

        now = datetime.now(timezone(timedelta(hours=utc_offset)))
        formatted_date = now.strftime(f"%b {now.day}{lib.fmt.ordinal(now.day)}, %Y")

        await helper.interactions.handle_modes_renders(interaction, render_difference, {
            "name": name,
            "uuid": uuid,
            "relative_date": formatted_date,
            "method": tracker,
            "hypixel_data": hypixel_data,
            "skin_model": skin_model,
            "save_dir": interaction.id
        })


    @helper.decorators.app_command("difference_daily", group=difference_group)
    @helper.interactions.access_permitted_check()
    async def daily(self, interaction: discord.Interaction, player: str=None):
        await self.difference_command(interaction, player, 'daily')

    @helper.decorators.app_command("difference_weekly", group=difference_group)
    @helper.interactions.access_permitted_check()
    async def weekly(self, interaction: discord.Interaction, player: str=None):
        await self.difference_command(interaction, player, 'weekly')

    @helper.decorators.app_command("difference_monthly", group=difference_group)
    @helper.interactions.access_permitted_check()
    async def monthly(self, interaction: discord.Interaction, player: str=None):
        await self.difference_command(interaction, player, 'monthly')

    @helper.decorators.app_command("difference_yearly", group=difference_group)
    @helper.interactions.access_permitted_check()
    async def yearly(self, interaction: discord.Interaction, player: str=None):
        await self.difference_command(interaction, player, 'yearly')


async def setup(client: helper.Client) -> None:
    await client.add_cog(DifferenceCommandCog())
