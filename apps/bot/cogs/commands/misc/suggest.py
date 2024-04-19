import discord
from discord import app_commands
from discord.ext import commands

import statalib as lib


class SubmitSuggestion(lib.CustomBaseModal, title='Submit Suggestion'):
    def __init__(self, channel: discord.TextChannel, **kwargs):
        self.channel = channel
        super().__init__(**kwargs)

    suggestion = discord.ui.TextInput(
        label='Suggestion:',
        placeholder='You should add...',
        style=discord.TextStyle.long
    )

    async def on_submit(self, interaction: discord.Interaction):
        await lib.run_interaction_checks(interaction)

        format_values = {
            'title': {
                'user': interaction.user,
                'discord_id': interaction.user.id
            },
            'fields': {
                0: {
                    'value': {
                        'suggestion': str(self.suggestion)
                    }
                }
            }
        }
        embeds = lib.load_embeds('suggestion', format_values, color='primary')

        await self.channel.send(embeds=embeds)
        await interaction.response.send_message(
            'Successfully submitted suggestion!', ephemeral=True)


class Suggest(commands.Cog):
    def __init__(self, client):
        self.client: commands.Bot = client


    @app_commands.command(
        name='suggest',
        description='Suggest a feature you would like to see added!')
    async def suggest(self, interaction: discord.Interaction):
        await lib.run_interaction_checks(interaction)

        channel_id = lib.config(
            'global.support_server.channels.suggestions_channel_id')
        channel = self.client.get_channel(channel_id)
        await interaction.response.send_modal(SubmitSuggestion(channel))

        lib.update_command_stats(interaction.user.id, 'suggest')


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Suggest(client))
