import discord
from discord.ext import commands

import statalib as lib
import helper
from render.displayname import render_displayname


class DisplayNameCommandCog(commands.Cog):
    @helper.decorators.app_command("displayname")
    @helper.interactions.access_permitted_check()
    async def displayname(
        self,
        interaction: discord.Interaction,
        player: str | None=None
    ):
        await interaction.response.defer()

        name, uuid = await helper.interactions.fetch_player_info(player, interaction)
        hypixel_data = await lib.network.fetch_hypixel_data(uuid)

        if not hypixel_data.get('player'):
            hypixel_data['player'] = {}

        rendered = await render_displayname(name, hypixel_data)
        await interaction.followup.send(
            files=[discord.File(rendered, filename="displayname.png")]
        )

async def setup(client: helper.Client) -> None:
    await client.add_cog(DisplayNameCommandCog())
