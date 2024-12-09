import discord
from discord import app_commands
from discord.ext import commands

import statalib as lib
import helper


class SubmitSuggestion(
    lib.shared_views.CustomBaseModal, title='Submit Suggestion'
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

        embed = lib.Embeds.misc.suggestion_message(
            str(interaction.user), interaction.user.id, str(self.suggestion))

        await self.channel.send(embed=embed)
        await interaction.response.send_message(
            'Successfully submitted suggestion!', ephemeral=True)


class Suggest(commands.Cog):
    def __init__(self, client):
        self.client: commands.Bot = client


    @app_commands.command(
        name='suggest',
        description='Suggest a feature you would like to see added!')
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    async def suggest(self, interaction: discord.Interaction):
        await helper.interactions.run_interaction_checks(interaction)

        channel_id = lib.config(
            'global.support_server.channels.suggestions_channel_id')
        channel = self.client.get_channel(channel_id)
        await interaction.response.send_modal(SubmitSuggestion(channel))

        lib.usage.update_command_stats(interaction.user.id, 'suggest')


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Suggest(client))
