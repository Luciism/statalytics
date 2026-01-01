import discord
from discord import app_commands
from discord.ext import commands

import statalib as lib
import helper


class Vote(commands.Cog):
    def __init__(self, client):
        self.client: commands.Bot = client


    @app_commands.command(name="vote", description="Get a list of our vote links")
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    async def vote(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await helper.interactions.run_interaction_checks(interaction)

        voting_data = lib.accounts.Account(interaction.user.id).voting.load()

        if voting_data.last_vote:
            last_vote_timestamp = f'<t:{int(voting_data.last_vote)}:R>'
        else:
            last_vote_timestamp = 'N/A'

        embed = helper.Embeds.misc.voting_info(last_vote_timestamp, voting_data.total_votes)

        await interaction.followup.send(embed=embed)
        lib.usage.update_command_stats(interaction.user.id, command='vote')


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Vote(client))
