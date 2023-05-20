import os
import sqlite3

import discord
from discord import app_commands
from discord.ext import commands

from ui import SelectView
from render.year import render_year
from functions import (username_autocompletion,
                       session_autocompletion,
                       check_subscription,
                       get_hypixel_data,
                       update_command_stats,
                       authenticate_user,
                       get_smart_session,
                       skin_session)


class Year(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.GENERATING_MESSAGE = 'Generating please wait <a:loading1:1062561739989860462>'

    # Milestone Stats
    @app_commands.command(name = "2024", description = "View the a players projected stats for 2024")
    @app_commands.autocomplete(username=username_autocompletion, session=session_autocompletion)
    @app_commands.describe(username='The player you want to view', session='The session you want to use')
    @app_commands.checks.dynamic_cooldown(check_subscription)
    async def year(self, interaction: discord.Interaction, username: str=None, session: int=None):
        try: name, uuid = await authenticate_user(username, interaction)
        except TypeError: return

        # Bot responses Logic
        refined = name.replace('_', r'\_')

        if session is None: session = 100
        session_data = await get_smart_session(interaction, session, refined, uuid)
        if not session_data: return
        if session == 100: session = session_data[0]

        await interaction.response.send_message(self.GENERATING_MESSAGE)
        os.makedirs(f'./database/activerenders/{interaction.id}')
        skin_res = skin_session.get(f'https://visage.surgeplay.com/bust/144/{uuid}', timeout=10)

        hypixel_data = get_hypixel_data(uuid)

        render_year(name, uuid, session, mode="Overall", hypixel_data=hypixel_data, skin_res=skin_res.content, save_dir=interaction.id)

        view = SelectView(user=interaction.user.id, inter=interaction, mode='Select a mode')

        await interaction.edit_original_response(content=None, attachments=[discord.File(f"./database/activerenders/{interaction.id}/overall.png")], view=view)
        render_year(name, uuid, session, mode="Solos", hypixel_data=hypixel_data, skin_res=skin_res.content, save_dir=interaction.id)
        render_year(name, uuid, session, mode="Doubles", hypixel_data=hypixel_data, skin_res=skin_res.content, save_dir=interaction.id)
        render_year(name, uuid, session, mode="Threes", hypixel_data=hypixel_data, skin_res=skin_res.content, save_dir=interaction.id)
        render_year(name, uuid, session, mode="Fours", hypixel_data=hypixel_data, skin_res=skin_res.content, save_dir=interaction.id)
        render_year(name, uuid, session, mode="4v4", hypixel_data=hypixel_data, skin_res=skin_res.content, save_dir=interaction.id)

        update_command_stats(interaction.user.id, 'year')

async def setup(client: commands.Bot) -> None:
    await client.add_cog(Year(client))
