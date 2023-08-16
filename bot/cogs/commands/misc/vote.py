import discord
from discord import app_commands
from discord.ext import commands

from statalib.functions import (
    update_command_stats,
    get_voting_data,
    get_config,
    load_embeds
)


class Vote(commands.Cog):
    def __init__(self, client):
        self.client: commands.Bot = client


    @app_commands.command(name="vote", description="Get a list of our vote links")
    async def vote(self, interaction: discord.Interaction):
        await interaction.response.defer()

        vote_links = get_config()['links']['voting']

        voting_data = get_voting_data(interaction.user.id)
        if voting_data:
            total_votes = voting_data[1]
            last_vote = voting_data[3]
            last_vote_timestamp = f'<t:{int(last_vote)}:R>'
        else:
            total_votes = 0
            last_vote_timestamp = 'N/A'

        format_values = {
            'top_gg': vote_links["top.gg"],
            'discordbotlist_com': vote_links["discordbotlist.com"],
            'discords_com': vote_links["discords.com"],
            'last_vote': last_vote_timestamp,
            'total_votes': total_votes
        }

        embeds = load_embeds('vote', format_values, color='primary')

        await interaction.followup.send(embeds=embeds)
        update_command_stats(interaction.user.id, command='vote')


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Vote(client))
