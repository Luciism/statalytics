import discord
from discord import app_commands
from discord.ext import commands

import statalib as lib


class Invite(commands.Cog):
    def __init__(self, client):
        self.client: commands.Bot = client


    @app_commands.command(
        name='invite',
        description='Invite Statalytics to your server')
    async def invite(self, interaction: discord.Interaction):
        invite_url = lib.config('links.invite_url')

        await interaction.response.send_message(
            f'To add Statalytics to your server, click [here]({invite_url})')

        lib.update_command_stats(interaction.user.id, 'invite')


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Invite(client))
