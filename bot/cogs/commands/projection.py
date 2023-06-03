import os

import discord
from discord import app_commands
from discord.ext import commands

from helper.ui import ModesView
from render.projection import render_projection
from helper.functions import (username_autocompletion,
                       session_autocompletion,
                       get_command_cooldown,
                       get_hypixel_data,
                       update_command_stats,
                       get_smart_session,
                       authenticate_user,
                       fetch_skin_model)


class Projection(commands.Cog):
    def __init__(self, client):
        self.client: discord.Client = client
        self.GENERATING_MESSAGE = 'Generating please wait <a:loading1:1062561739989860462>'


    @app_commands.command(name = "prestige", description = "View the projected stats of a player")
    @app_commands.autocomplete(username=username_autocompletion, session=session_autocompletion)
    @app_commands.describe(username='The player you want to view',
                           prestige='The prestige you want to view',
                           session='The session you want to use as a benchmark (defaults to 1)')
    @app_commands.checks.dynamic_cooldown(get_command_cooldown)
    async def projected_stats(self, interaction: discord.Interaction, prestige: int=None, username: str=None, session: int=None):
        try: name, uuid = await authenticate_user(username, interaction)
        except TypeError: return

        refined = name.replace('_', r'\_')
        if session is None: session = 100
        session_data = await get_smart_session(interaction, session, refined, uuid)
        if not session_data: return
        if session == 100: session = session_data[0]

        await interaction.response.send_message(self.GENERATING_MESSAGE)
        os.makedirs(f'./database/activerenders/{interaction.id}')
        skin_res = fetch_skin_model(uuid, 144)

        hypixel_data = get_hypixel_data(uuid)
        if not prestige:
            if hypixel_data.get('player'):
                current_star = hypixel_data.get('player', {}).get('achievements', {}).get('bedwars_level', 0)
            else: current_star = 0
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

        current_star = render_projection(mode="Overall", **kwargs)
        view = ModesView(user=interaction.user.id, inter=interaction, mode='Select a mode')
        content = ":warning: THE LEVEL YOU ENTERED IS LOWER THAN THE CURRENT STAR! :warning:" if current_star > prestige else None
        await interaction.edit_original_response(
            content=content, attachments=[discord.File(f"./database/activerenders/{interaction.id}/overall.png")], view=view)

        render_projection(mode="Solos", **kwargs)
        render_projection(mode="Doubles", **kwargs)
        render_projection(mode="Threes", **kwargs)
        render_projection(mode="Fours", **kwargs)
        render_projection(mode="4v4", **kwargs)

        update_command_stats(interaction.user.id, 'projection')


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Projection(client))
