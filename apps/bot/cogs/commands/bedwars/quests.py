import asyncio

import discord
from discord.ext import commands

import statalib as lib
import helper
from render.quests import render_quests


class QuestsCommandCog(commands.Cog):
    @helper.decorators.app_command("quests")
    @helper.interactions.access_permitted_check()
    async def quests(self, interaction: discord.Interaction, player: str=None):
        await interaction.response.defer()

        name, uuid = await helper.interactions.fetch_player_info(player, interaction)

        await interaction.followup.send(lib.config.loading_message())

        skin_model, hypixel_data = await asyncio.gather(
            lib.network.fetch_skin_model(uuid, 144),
            lib.network.fetch_hypixel_data(uuid)
        )

        rendered = await render_quests(name, uuid, hypixel_data, skin_model)

        _ = await interaction.edit_original_response(
            content=None,
            attachments=[discord.File(rendered, filename='quests.png')]
        )


async def setup(client: helper.Client) -> None:
    await client.add_cog(QuestsCommandCog())
