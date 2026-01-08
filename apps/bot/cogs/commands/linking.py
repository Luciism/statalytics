import discord
from discord.ext import commands

from statalib.accounts import Account
import helper


class LinkingCommandCog(commands.Cog):
    @helper.decorators.app_command("link")
    @helper.interactions.access_permitted_check()
    async def link(self, interaction: discord.Interaction, player: str):
        await helper.interactions.linking_interaction(interaction, player)


    @helper.decorators.app_command("unlink")
    @helper.interactions.access_permitted_check()
    async def unlink(self, interaction: discord.Interaction):
        await interaction.response.defer()

        previous_uuid = Account(interaction.user.id).linking.unlink_account()

        if previous_uuid is None:
            message = "You don't have an account linked! In order to link use `/link`!"
        else:
            message = 'Successfully unlinked your account!'

        await interaction.followup.send(message)


async def setup(client: helper.Client) -> None:
    await client.add_cog(LinkingCommandCog())
