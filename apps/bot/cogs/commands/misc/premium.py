import discord
from discord import app_commands
from discord.ext import commands

import statalib as lib


class Premium(commands.Cog):
    def __init__(self, client):
        self.client: commands.Bot = client


    @app_commands.command(
        name="premium",
        description="Information on statalytics premium")
    async def premium_command(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await lib.run_interaction_checks(interaction)

        await interaction.followup.send(
            embeds=lib.load_embeds("premium", color="primary"),
            view=lib.views.PremiumInfoView()
        )

        lib.update_command_stats(discord_id=interaction.user.id, command='premium')


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Premium(client))
