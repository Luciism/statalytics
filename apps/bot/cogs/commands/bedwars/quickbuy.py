import asyncio

import discord
import statalib as lib
from discord.ext import commands

import helper
from helper import app_command
from render.quickbuy import render_quickbuy


class QuickBuy(commands.Cog):
    def __init__(self, client: helper.Client):
        self.client: helper.Client = client
        self.LOADING_MSG: str = lib.config.loading_message()

        self.deprecation_warning: str = (
            "<:docs:1325495671272374272> **Warning:** "
            + "this command is deprecated. Please use `/quickbuy` instead."
        )

    async def quickbuy_command(
        self, interaction: discord.Interaction, player: str
    ) -> None:
        await interaction.response.defer()
        await helper.interactions.run_interaction_checks(interaction)

        name, uuid = await helper.interactions.fetch_player_info(player, interaction)

        await interaction.followup.send(self.LOADING_MSG)

        skin_model, hypixel_data = await asyncio.gather(
            lib.network.fetch_skin_model(uuid, 252, style="full"),
            lib.network.fetch_hypixel_data(uuid),
        )
        hypixel_data = await lib.network.fetch_hypixel_data(uuid)
        rendered = await render_quickbuy(name, uuid, hypixel_data, skin_model)

        _ = await interaction.edit_original_response(
            content=None, attachments=[discord.File(rendered, filename="quickbuy.png")]
        )

    @app_command("shop", "[DEPRECATED] View the shopkeeper layout of a player", {
        "player": "The player you want to view"})
    async def shop(self, interaction: discord.Interaction, player: str = None):
        await self.quickbuy_command(interaction, player)
        _ = await interaction.edit_original_response(content=self.deprecation_warning)
        lib.usage.update_command_stats(interaction.user.id, "shop")

    @app_command("hotbar", "[DEPRECATED] View the hotbar layout of a player", {
        "player": "The player you want to view"})
    async def hotbar(self, interaction: discord.Interaction, player: str = None):
        await self.quickbuy_command(interaction, player)
        _ = await interaction.edit_original_response(content=self.deprecation_warning)
        lib.usage.update_command_stats(interaction.user.id, "hotbar")


    @app_command("quickbuy", "View the quickbuy layout of a player", {
        "player": "The player you would like to lookup"})
    async def quickbuy(self, interaction: discord.Interaction, player: str = None):
        await self.quickbuy_command(interaction, player)
        lib.usage.update_command_stats(interaction.user.id, "quickbuy")


async def setup(client: helper.Client) -> None:
    await client.add_cog(QuickBuy(client))

