import discord
from discord import app_commands
from discord.ext import commands

from statalib import handle_interaction_errors


class ErrorHandling(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client: commands.Bot = client

        @client.tree.error
        async def on_tree_error(
            interaction: discord.Interaction,
            error: app_commands.AppCommandError
        ):
            await handle_interaction_errors(interaction, error)


    @commands.Cog.listener()
    async def on_command_error(self, _, error):
        if isinstance(error, commands.errors.CommandNotFound):
            return
        raise error


async def setup(client: commands.Bot) -> None:
    await client.add_cog(ErrorHandling(client))
