import discord
from discord import app_commands
from discord.ext import commands

import statalib as lib
import helper


class Credits(commands.Cog):
    def __init__(self, client):
        self.client: commands.Bot = client


    @app_commands.command(
        name="credits",
        description="The slaves that made Statalytics possible")
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    async def credits(self, interaction: discord.Interaction):
        await helper.interactions.run_interaction_checks(interaction)

        embed = lib.Embeds.misc.credits()
        await interaction.response.send_message(embed=embed)

        lib.usage.update_command_stats(interaction.user.id, 'credits')


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Credits(client))
