import asyncio

import discord
import statalib as lib
from discord import app_commands
from discord.ext import commands

import helper
from render.quickbuy import render_quickbuy


class QuickBuy(commands.Cog):
    def __init__(self, client):
        self.client: commands.Bot = client
        self.LOADING_MSG = lib.config.loading_message()

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

    @app_commands.command(name="shop", description="[DEPRECATED] View the shopkeeper of a player")
    @app_commands.describe(player="The player you want to view")
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.autocomplete(player=helper.username_autocompletion)
    @app_commands.checks.dynamic_cooldown(helper.generic_command_cooldown)
    async def shop(self, interaction: discord.Interaction, player: str = None):
        await self.quickbuy_command(interaction, player)
        _ = await interaction.edit_original_response(content=self.deprecation_warning)
        lib.usage.update_command_stats(interaction.user.id, "shop")

    @app_commands.command(
        name="hotbar",
        description="[DEPRECATED] View the hotbar preferences of a player")
    @app_commands.describe(player='The player you want to view')
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.autocomplete(player=helper.username_autocompletion)
    @app_commands.checks.dynamic_cooldown(helper.generic_command_cooldown)
    async def hotbar(self, interaction: discord.Interaction, player: str = None):
        await self.quickbuy_command(interaction, player)
        _ = await interaction.edit_original_response(content=self.deprecation_warning)
        lib.usage.update_command_stats(interaction.user.id, "hotbar")

    @app_commands.command(
        name="quickbuy", description="View the quickbuy layout of a player"
    )
    @app_commands.describe(player="The player you want to view")
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.autocomplete(player=helper.username_autocompletion)
    @app_commands.checks.dynamic_cooldown(helper.generic_command_cooldown)
    async def quickbuy(self, interaction: discord.Interaction, player: str = None):
        await self.quickbuy_command(interaction, player)
        lib.usage.update_command_stats(interaction.user.id, "quickbuy")


async def setup(client: commands.Bot) -> None:
    await client.add_cog(QuickBuy(client))
