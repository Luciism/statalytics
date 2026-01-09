import discord
from discord import app_commands
from discord.ext import commands

import helper


class ErrorHandlingCog(commands.Cog):
    def __init__(self, client: helper.Client):

        @client.tree.error
        async def _(
            interaction: discord.Interaction,
            error: app_commands.AppCommandError
        ):
            await helper.handlers.handle_interaction_errors(interaction, error)


    @commands.Cog.listener()
    async def on_command_error(self, _, error: commands.errors.CommandError):
        if isinstance(error, commands.errors.CommandNotFound):
            return
        raise error


async def setup(client: helper.Client) -> None:
    await client.add_cog(ErrorHandlingCog(client))
