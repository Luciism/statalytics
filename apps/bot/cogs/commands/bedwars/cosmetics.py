import discord
from discord.ext import commands

import statalib as lib
import helper
from render.cosmetics import render_cosmetics


class CosmeticsCommandCog(commands.Cog):
    @helper.decorators.app_command("cosmetics")
    @helper.interactions.access_permitted_check()
    async def active_cosmetics(
        self,
        interaction: discord.Interaction,
        player: str=None
    ):
        await interaction.response.defer()

        name, uuid = await helper.interactions.fetch_player_info(player, interaction)
        await interaction.followup.send(lib.config.loading_message())

        hypixel_data = await lib.network.fetch_hypixel_data(uuid)
        rendered = await render_cosmetics(name, uuid, hypixel_data)

        _ = await interaction.edit_original_response(
            content=None,
            attachments=[discord.File(rendered, filename='cosmetics.png')]
        )


async def setup(client: helper.Client) -> None:
    await client.add_cog(CosmeticsCommandCog())
