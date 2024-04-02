import discord
from discord import app_commands
from discord.ext import commands

import statalib as lib


class Linking(commands.Cog):
    def __init__(self, client):
        self.client: commands.Bot = client


    @app_commands.command(name="link", description="Link your account")
    @app_commands.checks.dynamic_cooldown(lib.generic_command_cooldown)
    @app_commands.describe(player='The player you want to link to')
    async def link(self, interaction: discord.Interaction, player: str):
        await lib.linking_interaction(interaction, player)
        lib.update_command_stats(interaction.user.id, 'link')


    @app_commands.command(name="unlink", description="Unlink your account")
    async def unlink(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await lib.run_interaction_checks(interaction)

        previous_uuid = lib.delete_linked_data(interaction.user.id)

        if previous_uuid is None:
            message = "You don't have an account linked! In order to link use `/link`!"
        else:
            message = 'Successfully unlinked your account!'

        await interaction.followup.send(message)
        lib.update_command_stats(interaction.user.id, 'unlink')


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Linking(client))
