import asyncio

import discord
from discord.ext import commands

import statalib as lib

import helper
from helper.decorators import app_command
from render.average import render_average


class AverageCommandCog(commands.Cog):
    @app_command(command_id="average")
    @helper.interactions.access_permitted_check()
    async def average(self, interaction: discord.Interaction, player: str=None):
        await interaction.response.defer()

        name, uuid = await helper.interactions.fetch_player_info(player, interaction)

        await interaction.followup.send(lib.config.loading_message())

        skin_model, hypixel_data = await asyncio.gather(
            lib.network.fetch_skin_model(uuid, 144),
            lib.network.fetch_hypixel_data(uuid)
        )

        await helper.interactions.handle_modes_renders(interaction, render_average, {
            "name": name,
            "uuid": uuid,
            "hypixel_data": hypixel_data,
            "skin_model": skin_model,
            "save_dir": interaction.id
        })


async def setup(client: helper.Client) -> None:
    await client.add_cog(AverageCommandCog())
