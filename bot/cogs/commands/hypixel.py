import os
import requests
from time import time

import discord
from discord import app_commands
from discord.ext import commands

from helper.functions import (
    get_command_cooldown,
    update_command_stats
)


class Compare(commands.Cog):
    def __init__(self, client):
        self.client: discord.Client = client

        self.key = os.environ.get('POLSU_KEY')


    status = app_commands.Group(name='status', description='Status Group Command')


    @status.command(name="hypixel", description="Hypixel's real-time status")
    @app_commands.checks.dynamic_cooldown(get_command_cooldown)
    async def status_hypixel(self, interaction: discord.Interaction):
        await interaction.response.defer()

        try:
            d: dict = requests.get(f"https://api.polsu.xyz/polsu/minecraft/server?key={self.key}&ip=mc.hypixel.net", timeout=10).json()
        except:
            # In case the API doesn't respond or reponds with HTML instead of JSON.
            d = {"success": False}
        
        # Generating a unique timestamp & image url to avoid Discord's image cache.
        t: int = int(time())

        if d["success"]:
            data = d["data"]

            embeds = []
            embed = discord.Embed(title=f"Bedwars Practice Info", description=f"BWP's current server information.\n\n**` > ` Status**: `{'Online' if data['online'] else 'Offline'}`\n**` > ` IP**: **`{data['ip']}`**\n**` > ` Version**: `{data['version']}`\n\n**` > ` Updated**: <t:{data['time']['last']}>", colour=0x2f3136)
            embed.set_image(url=f'{data["image"]["motd"]}?t={t}')
            embed.set_thumbnail(url=f'{data["image"]["icon"]}?t={t}')
            embed.set_footer(text=f"Powered by Polsu's API - https://api.polsu.xyz")
            embeds.append(embed)

            embed = discord.Embed(title="Ping", description=f"**` > ` Ping**: `{data['ping']['last']}`\n\n**` > ` Max**: `{data['ping']['max']}`\n**` > ` Average**: `{data['ping']['average']}`\n**` > ` Min**: `{data['ping']['min']}`\n", colour=0x2f3136)
            embed.set_image(url=f'{data["image"]["ping"]}?t={t}')
            embed.set_footer(text=f"UTC Time  -  Ping in ms (USA - Los Angeles)")
            embeds.append(embed)

            embed = discord.Embed(title="Players", description=f"**` > ` Players**: `{data['players']['current']}/{data['players']['server_max']}`\n\n**` > ` Max**: `{data['players']['max']}`\n**` > ` Average**: `{data['players']['average']}`\n**` > ` Min**: `{data['players']['min']}`\n", colour=0x2f3136)
            embed.set_image(url=f'{data["image"]["players"]}?t={t}')
            embed.set_footer(text=f"Hypixel Status")
            embeds.append(embed)

            await interaction.response.send_message(embeds=embeds)
        else:
            await interaction.response.send_message(content=f"Something went wrong...\nCouldn't load the data.", ephemeral=True)

        update_command_stats(interaction.user.id, 'status_hypixel')


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Compare(client))
