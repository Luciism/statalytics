import asyncio

import discord
import statalib as lib
from discord.ext import commands

import helper
from render.quickbuy import render_quickbuy


class QuickBuyCommandCog(commands.Cog):
    DEPRECATION_WARNING: str = (
        "<:docs:1325495671272374272> **Warning:** "
        + "this command is deprecated. Please use `/quickbuy` instead."
    )

    async def quickbuy_command(
        self, interaction: discord.Interaction, player: str | None
    ) -> None:
        await interaction.response.defer()

        name, uuid = await helper.interactions.fetch_player_info(player, interaction)

        await interaction.followup.send(lib.config.loading_message())

        skin_model, hypixel_data = await asyncio.gather(
            lib.network.fetch_skin_model(uuid, style="fullbody"),
            lib.network.fetch_hypixel_data(uuid),
        )
        hypixel_data = await lib.network.fetch_hypixel_data(uuid)
        rendered = await render_quickbuy(name, uuid, hypixel_data, skin_model)

        _ = await interaction.edit_original_response(
            content=None, attachments=[discord.File(rendered, filename="quickbuy.png")]
        )


    @helper.decorators.app_command("shop")
    @helper.interactions.access_permitted_check()
    async def shop(self, interaction: discord.Interaction, player: str | None=None):
        await self.quickbuy_command(interaction, player)
        _ = await interaction.edit_original_response(content=self.DEPRECATION_WARNING)


    @helper.decorators.app_command("hotbar")
    @helper.interactions.access_permitted_check()
    async def hotbar(self, interaction: discord.Interaction, player: str | None=None):
        await self.quickbuy_command(interaction, player)
        _ = await interaction.edit_original_response(content=self.DEPRECATION_WARNING)


    @helper.decorators.app_command("quickbuy")
    @helper.interactions.access_permitted_check()
    async def quickbuy(self, interaction: discord.Interaction, player: str | None=None):
        await self.quickbuy_command(interaction, player)


async def setup(client: helper.Client) -> None:
    await client.add_cog(QuickBuyCommandCog())

