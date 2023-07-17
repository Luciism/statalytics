import discord
from discord import app_commands
from discord.ext import commands

from statalib.functions import (
    update_command_stats,
    load_embeds,
    STATIC_CONFIG
)


class SubmitSuggestion(discord.ui.Modal, title='Submit Suggestion'):
    def __init__(self, channel: discord.TextChannel, **kwargs):
        self.channel = channel
        super().__init__(**kwargs)

    suggestion = discord.ui.TextInput(
        label='Suggestion:',
        placeholder='You should add...',
        style=discord.TextStyle.long
    )

    async def on_submit(self, interaction: discord.Interaction):
        format_values = {
            'user': interaction.user,
            'discord_id': interaction.user.id,
            'suggestion': str(self.suggestion)
        }
        embeds = load_embeds('suggestion', format_values, color='primary')

        await self.channel.send(embeds=embeds)
        await interaction.response.send_message('Successfully submitted suggestion!', ephemeral=True)


class Suggest(commands.Cog):
    def __init__(self, client):
        self.client: discord.Client = client


    @app_commands.command(name='suggest', description='Suggest a feature you would like to see added!')
    async def suggest(self, interaction: discord.Interaction):
        channel_id = STATIC_CONFIG.get('suggestions_channel_id')
        channel = self.client.get_channel(channel_id)
        await interaction.response.send_modal(SubmitSuggestion(channel))

        update_command_stats(interaction.user.id, 'suggest')


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Suggest(client))
