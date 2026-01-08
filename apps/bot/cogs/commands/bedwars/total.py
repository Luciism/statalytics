import asyncio
from typing import Callable

import discord
import statalib as lib
from discord.ext import commands

import helper
from render.pointless import render_pointless
from render.total import render_total


class GenericStatsCommandCog(commands.Cog):
    async def total_command(
        self,
        interaction: discord.Interaction,
        player: str,
        render_func: Callable,
        dreams: bool = False,
    ):
        await interaction.response.defer()

        name, uuid = await helper.interactions.fetch_player_info(player, interaction)

        await interaction.followup.send(lib.config.loading_message())

        skin_model, hypixel_data = await asyncio.gather(
            lib.network.fetch_skin_model(uuid, 144),
            lib.network.fetch_hypixel_data(uuid),
        )

        kwargs = {
            "name": name,
            "uuid": uuid,
            "hypixel_data": hypixel_data,
            "skin_model": skin_model,
            "save_dir": interaction.id,
        }

        await helper.interactions.handle_modes_renders(
            interaction, render_func, kwargs, dreams=dreams
        )

    @helper.decorators.app_command("generic")
    @helper.interactions.access_permitted_check()
    async def total(self, interaction: discord.Interaction, player: str = None):
        await self.total_command(
            interaction, player, render_func=render_total
        )


    @helper.decorators.app_command("pointless")
    @helper.interactions.access_permitted_check()
    async def pointless(self, interaction: discord.Interaction, player: str = None):
        await self.total_command(
            interaction, player, render_func=render_pointless
        )


    @helper.decorators.app_command("dreams")
    @helper.interactions.access_permitted_check()
    async def dreams(self, interaction: discord.Interaction, player: str = None):
        await self.total_command(
            interaction, player, render_func=render_total, dreams=True
        )


async def setup(client: helper.Client) -> None:
    await client.add_cog(GenericStatsCommandCog())
