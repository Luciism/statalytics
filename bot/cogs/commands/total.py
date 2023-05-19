import os

import discord
from discord import app_commands
from discord.ext import commands

from ui import SelectView
from render.rendertotal import rendertotal
from functions import (username_autocompletion,
                       check_subscription,
                       get_hypixel_data,
                       update_command_stats,
                       authenticate_user,
                       skin_session)


class Total(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.GENERATING_MESSAGE = 'Generating please wait <a:loading1:1062561739989860462>'

    # Total stats
    @app_commands.command(name = "bedwars", description = "View the general stats of a player")
    @app_commands.autocomplete(username=username_autocompletion)
    @app_commands.describe(username='The player you want to view')
    @app_commands.checks.dynamic_cooldown(check_subscription)
    async def total(self, interaction: discord.Interaction, username: str=None):
        try: name, uuid = await authenticate_user(username, interaction)
        except TypeError: return

        await interaction.response.send_message(self.GENERATING_MESSAGE)
        os.makedirs(f'./database/activerenders/{interaction.id}')
        skin_res = skin_session.get(f'https://visage.surgeplay.com/bust/144/{uuid}', timeout=10)
        hypixel_data = get_hypixel_data(uuid)

        rendertotal(name, uuid, mode="Overall", hypixel_data=hypixel_data, skin_res=skin_res.content, save_dir=interaction.id, method="generic")
        view = SelectView(user=interaction.user.id, inter=interaction, mode='Select a mode')
        await interaction.edit_original_response(content=None, attachments=[discord.File(f"./database/activerenders/{interaction.id}/overall.png")], view=view)
        rendertotal(name, uuid, mode="Solos", hypixel_data=hypixel_data, skin_res=skin_res.content, save_dir=interaction.id, method="generic")
        rendertotal(name, uuid, mode="Doubles", hypixel_data=hypixel_data, skin_res=skin_res.content, save_dir=interaction.id, method="generic")
        rendertotal(name, uuid, mode="Threes", hypixel_data=hypixel_data, skin_res=skin_res.content, save_dir=interaction.id, method="generic")
        rendertotal(name, uuid, mode="Fours", hypixel_data=hypixel_data, skin_res=skin_res.content, save_dir=interaction.id, method="generic")
        rendertotal(name, uuid, mode="4v4", hypixel_data=hypixel_data, skin_res=skin_res.content, save_dir=interaction.id, method="generic")

        update_command_stats(interaction.user.id, 'total')

    # Pointless stats
    @app_commands.command(name = "pointless", description = "View the general pointless stats of a player")
    @app_commands.autocomplete(username=username_autocompletion)
    @app_commands.describe(username='The player you want to view')
    @app_commands.checks.dynamic_cooldown(check_subscription)
    async def pointless(self, interaction: discord.Interaction, username: str=None):
        try: name, uuid = await authenticate_user(username, interaction)
        except TypeError: return

        await interaction.response.send_message(self.GENERATING_MESSAGE)
        os.makedirs(f'./database/activerenders/{interaction.id}')
        skin_res = skin_session.get(f'https://visage.surgeplay.com/bust/144/{uuid}', timeout=10)
        hypixel_data = get_hypixel_data(uuid)

        rendertotal(name, uuid, mode="Overall", hypixel_data=hypixel_data, skin_res=skin_res.content, save_dir=interaction.id, method="pointless")
        view = SelectView(user=interaction.user.id, inter=interaction, mode='Select a mode')
        await interaction.edit_original_response(content=None, attachments=[discord.File(f"./database/activerenders/{interaction.id}/overall.png")], view=view)
        rendertotal(name, uuid, mode="Solos", hypixel_data=hypixel_data, skin_res=skin_res.content, save_dir=interaction.id, method="pointless")
        rendertotal(name, uuid, mode="Doubles", hypixel_data=hypixel_data, skin_res=skin_res.content, save_dir=interaction.id, method="pointless")
        rendertotal(name, uuid, mode="Threes", hypixel_data=hypixel_data, skin_res=skin_res.content, save_dir=interaction.id, method="pointless")
        rendertotal(name, uuid, mode="4v4", hypixel_data=hypixel_data, skin_res=skin_res.content, save_dir=interaction.id, method="pointless")

        update_command_stats(interaction.user.id, 'pointless')

async def setup(client: commands.Bot) -> None:
    await client.add_cog(Total(client))
