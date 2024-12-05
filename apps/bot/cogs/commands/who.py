import discord
from discord import app_commands
from discord.ext import commands

import statalib as lib
import helper


class Who(commands.Cog):
    def __init__(self, client):
        self.client: commands.Bot = client


    @app_commands.command(
        name="who",
        description="Convert the name of uuid of a player")
    @app_commands.describe(
        player='The player whos username / uuid you want to view')
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    async def who(self, interaction: discord.Interaction,
                  player: str=None):
        await helper.interactions.run_interaction_checks(interaction)

        name, uuid = await helper.interactions.fetch_player_info(player, interaction, eph=True)

        if player is None or len(player) <= 16:
            await interaction.response.send_message(
                f'UUID for **{name}** -> `{uuid}`', ephemeral=True)
        else:
            await interaction.response.send_message(
                f'Name for **{uuid}** -> `{name}`', ephemeral=True)

        lib.usage.update_command_stats(interaction.user.id, 'who')


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Who(client))
