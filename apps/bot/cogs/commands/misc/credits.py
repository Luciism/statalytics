import discord
from discord import app_commands
from discord.ext import commands

import statalib as lib


class Credits(commands.Cog):
    def __init__(self, client):
        self.client: commands.Bot = client


    @app_commands.command(
        name="credits",
        description="The slaves that made Statalytics possible")
    async def credits(self, interaction: discord.Interaction):
        await lib.run_interaction_checks(interaction)

        embeds = lib.load_embeds('credits', color='primary')
        await interaction.response.send_message(embeds=embeds)

        lib.update_command_stats(interaction.user.id, 'credits')


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Credits(client))
