import discord
from discord.ext import commands

import statalib as lib
import helper
from render.resources import render_resources


class ResourcesCommandCog(commands.Cog):
    @helper.decorators.app_command("resources")
    @helper.interactions.access_permitted_check()
    async def resources(self, interaction: discord.Interaction, player: str=None):
        await interaction.response.defer()

        name, uuid = await helper.interactions.fetch_player_info(player, interaction)

        await interaction.followup.send(lib.config.loading_message())
        hypixel_data = await lib.network.fetch_hypixel_data(uuid)

        await helper.interactions.handle_modes_renders(interaction, render_resources, {
            "name": name,
            "uuid": uuid,
            "hypixel_data": hypixel_data,
            "save_dir": interaction.id
        })


async def setup(client: helper.Client) -> None:
    await client.add_cog(ResourcesCommandCog())
