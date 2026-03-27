from io import BytesIO

import discord
from discord.ext import commands

import statalib as lib
import helper


class SkinCommandCog(commands.Cog):
    @helper.decorators.app_command("skin")
    @helper.interactions.access_permitted_check()
    async def skin(self, interaction: discord.Interaction, player: str=None):
        await interaction.response.defer()

        name, uuid = await helper.interactions.fetch_player_info(player, interaction)

        image_bytes = await lib.network.fetch_skin_model(uuid, style='fullbody')

        embed = helper.Embeds.misc.player_skin(lib.fmt.fname(name), uuid)

        file = discord.File(BytesIO(image_bytes), filename='skin.png')
        await interaction.followup.send(file=file, embed=embed)


async def setup(client: helper.Client) -> None:
    await client.add_cog(SkinCommandCog())
