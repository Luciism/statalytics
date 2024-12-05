import discord
from discord import app_commands
from discord.ext import commands

import statalib as lib
import helper


class Premium(commands.Cog):
    def __init__(self, client):
        self.client: commands.Bot = client


    @app_commands.command(
        name="premium",
        description="Information on statalytics premium")
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    async def premium_command(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await helper.interactions.run_interaction_checks(interaction)

        await interaction.followup.send(
            embeds=lib.load_embeds("premium", color="primary"),
            view=helper.views.PremiumInfoView()
        )

        lib.usage.update_command_stats(discord_id=interaction.user.id, command='premium')


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Premium(client))
