import discord
from discord.ext import commands

import statalib as lib
import helper


class VoteCommandCog(commands.Cog):
    @helper.decorators.app_command("vote")
    @helper.interactions.access_permitted_check()
    async def vote(self, interaction: discord.Interaction):
        await interaction.response.defer()

        voting_data = lib.accounts.Account(interaction.user.id).voting.load()

        if voting_data.last_vote:
            last_vote_timestamp = f'<t:{int(voting_data.last_vote)}:R>'
        else:
            last_vote_timestamp = 'N/A'

        embed = helper.Embeds.misc.voting_info(last_vote_timestamp, voting_data.total_votes)

        await interaction.followup.send(embed=embed)


async def setup(client: helper.Client) -> None:
    await client.add_cog(VoteCommandCog())
