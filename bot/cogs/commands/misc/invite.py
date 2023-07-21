import discord
from discord import app_commands
from discord.ext import commands

from statalib.functions import update_command_stats, get_config


class Invite(commands.Cog):
    def __init__(self, client):
        self.client: discord.Client = client


    @app_commands.command(
        name='invite',
        description='Invite Statalytics to your server')
    async def invite(self, interaction: discord.Interaction):
        invite_url = get_config()['links']['invite_url']

        await interaction.response.send_message(
            f'To add Statalytics to your server, click [here]({invite_url})')

        update_command_stats(interaction.user.id, 'invite')


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Invite(client))
