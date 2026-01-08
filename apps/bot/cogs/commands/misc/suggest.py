import discord
from discord.ext import commands

import statalib as lib
import helper


class SubmitSuggestion(
    helper.views.CustomBaseModal, title='Submit Suggestion'
):
    def __init__(self, channel: discord.TextChannel, **kwargs):
        self.channel = channel
        super().__init__(**kwargs)

    suggestion = discord.ui.TextInput(
        label='Suggestion:',
        placeholder='You should add...',
        style=discord.TextStyle.long
    )

    async def on_submit(self, interaction: discord.Interaction):
        await helper.interactions.run_interaction_checks(interaction)

        embed = helper.Embeds.misc.suggestion_message(
            str(interaction.user), interaction.user.id, str(self.suggestion))

        await self.channel.send(embed=embed)
        await interaction.response.send_message(
            'Successfully submitted suggestion!', ephemeral=True)


class SuggestCommandCog(commands.Cog):
    def __init__(self, client: helper.Client):
        self.client: helper.Client = client


    @helper.decorators.app_command("suggest")
    @helper.interactions.access_permitted_check()
    async def suggest(self, interaction: discord.Interaction):
        channel_id = lib.config(
            'global.support_server.channels.suggestions_channel_id')
        channel = self.client.get_channel(channel_id)
        await interaction.response.send_modal(SubmitSuggestion(channel))


async def setup(client: helper.Client) -> None:
    await client.add_cog(SuggestCommandCog(client))
