import discord
from discord.ext import commands

import statalib as lib
import helper


class InviteCommandCog(commands.Cog):
    @helper.decorators.app_command("invite")
    @helper.interactions.access_permitted_check()
    async def invite(self, interaction: discord.Interaction):
        invite_url = lib.config('global.links.invite_url')

        await interaction.response.send_message(
            f'To add Statalytics to your server, [click here]({invite_url})')


async def setup(client: helper.Client) -> None:
    await client.add_cog(InviteCommandCog())
