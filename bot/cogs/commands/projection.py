import os

import discord
from discord import app_commands
from discord.ext import commands

from render.projection import render_projection
from helper.functions import (username_autocompletion,
                       session_autocompletion,
                       get_command_cooldown,
                       get_hypixel_data,
                       update_command_stats,
                       get_smart_session,
                       authenticate_user,
                       fetch_skin_model,
                       send_generic_renders,
                       loading_message)


class Projection(commands.Cog):
    def __init__(self, client):
        self.client: discord.Client = client
        self.LOADING_MSG = loading_message()


    @app_commands.command(name = "prestige", description = "View the projected stats of a player")
    @app_commands.autocomplete(username=username_autocompletion, session=session_autocompletion)
    @app_commands.describe(username='The player you want to view',
                           prestige='The prestige you want to view',
                           session='The session you want to use as a benchmark (defaults to 1)')
    @app_commands.checks.dynamic_cooldown(get_command_cooldown)
    async def projected_stats(self, interaction: discord.Interaction, prestige: int=None, username: str=None, session: int=100):
        try: name, uuid = await authenticate_user(username, interaction)
        except TypeError: return
        refined = name.replace('_', r'\_')

        session_data = await get_smart_session(interaction, session, refined, uuid)
        if not session_data:
            return
        if session == 100:
            session = session_data[0]

        await interaction.response.send_message(self.LOADING_MSG)
        os.makedirs(f'./database/activerenders/{interaction.id}')
        skin_res = fetch_skin_model(uuid, 144)

        hypixel_data = get_hypixel_data(uuid)
        if not prestige:
            if hypixel_data.get('player'):
                current_star = hypixel_data.get('player', {}).get('achievements', {}).get('bedwars_level', 0)
            else:
                current_star = 0
            prestige = (current_star // 100 + 1) * 100
        if prestige <= 0: prestige = 1

        kwargs = {
            "name": name,
            "uuid": uuid,
            "session": session,
            "target": prestige,
            "hypixel_data": hypixel_data,
            "skin_res": skin_res,
            "save_dir": interaction.id
        }

        await send_generic_renders(interaction, render_projection, kwargs)
        update_command_stats(interaction.user.id, 'projection')


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Projection(client))
