import json

from datetime import datetime, timezone
from tzlocal import get_localzone

import discord
from discord import app_commands
from discord.ext import commands

from helper.functions import update_command_stats, get_voting_data

class Voting(commands.Cog):
    def __init__(self, client):
        self.client: discord.Client = client

    @app_commands.command(name = "vote", description = "Get a list of our vote links")
    async def vote(self, interaction: discord.Interaction):
        with open('./config.json', 'r') as datafile:
            config = json.load(datafile)
        vote_links = config['links']['voting']
        embed_color = int(config['embed_primary_color'], base=16)

        embed = discord.Embed(title='Vote For Statalytics', description='Voting helps Statalytics grow by increasing public exposure.', color=embed_color)
        embed.add_field(name='Links', value=f"""
            Vote on [top.gg]({vote_links["top.gg"]})
            Vote on [discordbotlist.com]({vote_links["discordbotlist.com"]})
            Vote on [discords.com]({vote_links["discords.com"]})
        """.replace('   ', ''), inline=False)

        embed.add_field(
            name='Rewards',
            value=f"""
                Theme packs for 24 hours.
                Cooldowns reduced by 50% (1.75s)

                *You can change your theme pack with `/settings`*
            """.replace('   ', ''),
            inline=False
        )

        voting_data = get_voting_data(interaction.user.id)
        if voting_data:
            total_votes = voting_data[1]
            last_vote = voting_data[3]
    
            last_vote_time = datetime.fromtimestamp(last_vote)
            last_vote_time = last_vote_time.replace(tzinfo=get_localzone())
            utc_datetime = last_vote_time.astimezone(timezone.utc)
            last_vote_timestamp = f'<t:{int(utc_datetime.timestamp())}:R>'
        else:
            total_votes = 0
            last_vote_timestamp = 'N/A'


        embed.add_field(
            name='Your History',
            value=f"""
                Last Vote: {last_vote_timestamp}
                Total Votes: {total_votes}
            """.replace('   ', ''),
            inline=False
        )

        await interaction.response.send_message(embed=embed)

        update_command_stats(interaction.user.id, command='vote')


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Voting(client))
