import discord
from discord.ext import commands

import statalib as lib
import helper
from render.mostplayed import render_mostplayed


class MostPlayedCommandCog(commands.Cog):
    @helper.decorators.app_command("gamemode_distributions")
    @helper.interactions.access_permitted_check()
    async def most_played(self, interaction: discord.Interaction, player: str | None=None):
        await interaction.response.defer()

        name, uuid = await helper.interactions.fetch_player_info(player, interaction)

        await interaction.followup.send(lib.config.loading_message())

        hypixel_data = await lib.network.fetch_hypixel_data(uuid)

        rendered = await render_mostplayed(name, uuid, hypixel_data)
        _ = await interaction.edit_original_response(
            content=None,
            attachments=[discord.File(rendered, filename='mostplayed.png')]
        )


async def setup(client: helper.Client) -> None:
    await client.add_cog(MostPlayedCommandCog())
