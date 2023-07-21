import discord
from discord import app_commands
from discord.ext import commands

from render.projection import render_projection
from statalib import (
    fetch_player_info,
    username_autocompletion,
    session_autocompletion,
    generic_command_cooldown,
    fetch_hypixel_data,
    update_command_stats,
    find_dynamic_session,
    fetch_skin_model,
    handle_modes_renders,
    loading_message
)


class Projection(commands.Cog):
    def __init__(self, client):
        self.client: discord.Client = client
        self.LOADING_MSG = loading_message()


    @app_commands.command(
        name="prestige",
        description="View the projected stats of a player")
    @app_commands.describe(
        username='The player you want to view',
        prestige='The prestige you want to view',
        session='The session you want to use as a benchmark (defaults to 1)')
    @app_commands.autocomplete(
        username=username_autocompletion,
        session=session_autocompletion)
    @app_commands.checks.dynamic_cooldown(generic_command_cooldown)
    async def projected_stats(self, interaction: discord.Interaction,
                              prestige: int=None, username: str=None, session: int=None):
        await interaction.response.defer()

        name, uuid = await fetch_player_info(username, interaction)

        session = await find_dynamic_session(interaction, name, uuid, session)

        await interaction.followup.send(self.LOADING_MSG)
        skin_res = await fetch_skin_model(uuid, 144)

        hypixel_data = await fetch_hypixel_data(uuid)
        if not prestige:
            if hypixel_data.get('player'):
                current_star = hypixel_data.get(
                    'player', {}).get('achievements', {}).get('bedwars_level', 0)
            else:
                current_star = 0
            prestige = (current_star // 100 + 1) * 100
        
        prestige = max(prestige, 1) # 1 or higher

        kwargs = {
            "name": name,
            "uuid": uuid,
            "session": session,
            "target": prestige,
            "hypixel_data": hypixel_data,
            "skin_res": skin_res,
            "save_dir": interaction.id
        }

        await handle_modes_renders(interaction, render_projection, kwargs)
        update_command_stats(interaction.user.id, 'projection')


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Projection(client))
