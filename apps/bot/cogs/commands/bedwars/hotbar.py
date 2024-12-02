import discord
from discord import app_commands
from discord.ext import commands

import statalib as lib
import helper
from render.hotbar import render_hotbar


class Hotbar(commands.Cog):
    def __init__(self, client):
        self.client: commands.Bot = client
        self.LOADING_MSG = lib.loading_message()


    @app_commands.command(
        name="hotbar",
        description="View the hotbar preferences of a player")
    @app_commands.describe(player='The player you want to view')
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.autocomplete(player=helper.username_autocompletion)
    @app_commands.checks.dynamic_cooldown(helper.generic_command_cooldown)
    async def hotbar(self, interaction: discord.Interaction, player: str=None):
        await interaction.response.defer()
        await helper.interactions.run_interaction_checks(interaction)

        name, uuid = await helper.interactions.fetch_player_info(player, interaction)

        await interaction.followup.send(self.LOADING_MSG)

        hypixel_data = await lib.network.fetch_hypixel_data(uuid)
        rendered = await render_hotbar(name, uuid, hypixel_data)
        await interaction.edit_original_response(
            content=None,
            attachments=[discord.File(rendered, filename="hotbar.png")]
        )

        lib.update_command_stats(interaction.user.id, 'hotbar')


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Hotbar(client))
