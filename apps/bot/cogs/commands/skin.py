from io import BytesIO

import discord
from discord import app_commands
from discord.ext import commands

import statalib as lib
import helper


class Skin(commands.Cog):
    def __init__(self, client):
        self.client: commands.Bot = client


    @app_commands.command(name="skin", description="View the skin of a player")
    @app_commands.autocomplete(player=helper.username_autocompletion)
    @app_commands.describe(player='The player you want to view')
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.checks.dynamic_cooldown(helper.generic_command_cooldown)
    async def skin(self, interaction: discord.Interaction, player: str=None):
        await interaction.response.defer()
        await helper.interactions.run_interaction_checks(interaction)

        name, uuid = await helper.interactions.fetch_player_info(player, interaction)

        image_bytes = await lib.network.fetch_skin_model(uuid, size=256, style='full')

        embed = helper.Embeds.misc.player_skin(lib.fmt.fname(name), uuid)

        file = discord.File(BytesIO(image_bytes), filename='skin.png')
        await interaction.followup.send(file=file, embed=embed)

        lib.usage.update_command_stats(interaction.user.id, 'skin')


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Skin(client))
