import discord
from discord import app_commands
from discord.ext import commands

import statalib as lib
from render.mostplayed import render_mostplayed


class MostPlayed(commands.Cog):
    def __init__(self, client):
        self.client: commands.Bot = client
        self.LOADING_MSG = lib.loading_message()


    @app_commands.command(
        name="mostplayed",
        description="Most played mode of a player")
    @app_commands.describe(player='The player you want to view')
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.autocomplete(player=lib.username_autocompletion)
    @app_commands.checks.dynamic_cooldown(lib.generic_command_cooldown)
    async def most_played(self, interaction: discord.Interaction ,player: str=None):
        await interaction.response.defer()
        await lib.run_interaction_checks(interaction)

        name, uuid = await lib.fetch_player_info(player, interaction)

        await interaction.followup.send(self.LOADING_MSG)

        hypixel_data = await lib.fetch_hypixel_data(uuid)

        rendered = await render_mostplayed(name, uuid, hypixel_data)
        await interaction.edit_original_response(
            content=None,
            attachments=[discord.File(rendered, filename='mostplayed.png')]
        )

        lib.update_command_stats(interaction.user.id, 'mostplayed')


async def setup(client: commands.Bot) -> None:
    await client.add_cog(MostPlayed(client))
