import discord
from discord.ext import commands

import statalib as lib
import helper
from render.compare import render_compare


class CompareCommandCog(commands.Cog):
    @helper.decorators.app_command(command_id="compare")
    @helper.interactions.access_permitted_check()
    async def compare(
        self,
        interaction: discord.Interaction,
        player_1: str,
        player_2: str=None
    ):
        await interaction.response.defer()

        name_1 = player_1 if player_2 else None
        name_2 = player_2 if player_2 else player_1

        name_1, uuid_1 = await helper.interactions.fetch_player_info(name_1, interaction)
        name_2, uuid_2 = await helper.interactions.fetch_player_info(name_2, interaction)

        await interaction.followup.send(lib.config.loading_message())
        hypixel_data_1 = await lib.network.fetch_hypixel_data(uuid_1)
        hypixel_data_2 = await lib.network.fetch_hypixel_data(uuid_2)

        await helper.interactions.handle_modes_renders(interaction, render_compare, {
            "name_1": name_1,
            "name_2": name_2,
            "uuid_1": uuid_1,
            "hypixel_data_1": hypixel_data_1,
            "hypixel_data_2": hypixel_data_2,
            "save_dir": interaction.id
        })


async def setup(client: helper.Client) -> None:
    await client.add_cog(CompareCommandCog())
