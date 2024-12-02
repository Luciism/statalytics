import asyncio

import discord
from discord import app_commands
from discord.ext import commands

import statalib as lib
import helper
from render.practice import render_practice


class Practice(commands.Cog):
    def __init__(self, client):
        self.client: commands.Bot = client
        self.LOADING_MSG = lib.loading_message()


    @app_commands.command(
        name="practice",
        description="View the practice stats of a player")
    @app_commands.describe(player='The player you want to view')
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.autocomplete(player=helper.username_autocompletion)
    @app_commands.checks.dynamic_cooldown(helper.generic_command_cooldown)
    async def practice(self, interaction: discord.Interaction,
                       player: str=None):
        await interaction.response.defer()
        await helper.interactions.run_interaction_checks(interaction)

        name, uuid = await helper.interactions.fetch_player_info(player, interaction)

        await interaction.followup.send(self.LOADING_MSG)

        skin_model, hypixel_data = await asyncio.gather(
            lib.network.fetch_skin_model(uuid, 144),
            lib.network.fetch_hypixel_data(uuid)
        )

        rendered = await render_practice(name, uuid, hypixel_data, skin_model)

        await interaction.edit_original_response(
            content=None,
            attachments=[discord.File(rendered, filename='practice.png')]
        )

        lib.update_command_stats(interaction.user.id, 'practice')


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Practice(client))
