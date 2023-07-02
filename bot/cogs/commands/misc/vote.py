import json

import discord
from discord import app_commands
from discord.ext import commands

from helper.functions import (
    update_command_stats,
    get_voting_data,
    get_embed_color,
    get_config
)


class Vote(commands.Cog):
    def __init__(self, client):
        self.client: discord.Client = client


    @app_commands.command(name="vote", description="Get a list of our vote links")
    async def vote(self, interaction: discord.Interaction):
        await interaction.response.defer()

        vote_links = get_config()['links']['voting']
        embed_color = get_embed_color('primary')

        voting_data = get_voting_data(interaction.user.id)
        if voting_data:
            total_votes = voting_data[1]
            last_vote = voting_data[3]
            last_vote_timestamp = f'<t:{int(last_vote)}:R>'
        else:
            total_votes = 0
            last_vote_timestamp = 'N/A'

        with open('./assets/embeds/vote.json', 'r') as datafile:
            vote_embed_str: str = json.load(datafile)['embeds'][0]

        vote_embed_str = vote_embed_str.format(
            embed_color=embed_color,
            top_gg=vote_links["top.gg"],
            discordbotlist_com=vote_links["discordbotlist.com"],
            discords_com=vote_links["discords.com"],
            last_vote=last_vote_timestamp,
            total_votes=total_votes
        ).replace("{{", "{").replace("}}", "}")

        embed = discord.Embed.from_dict(json.loads(vote_embed_str))

        await interaction.followup.send(embed=embed)
        update_command_stats(interaction.user.id, command='vote')


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Vote(client))
