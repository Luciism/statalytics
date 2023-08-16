# api.polsu.xyz

import time
from os import getenv

import requests
import discord
from discord import app_commands
from discord.ext import commands

from statalib import (
    generic_command_cooldown,
    update_command_stats,
    load_embeds,
    to_thread
)


@to_thread
def _fetch_server_status(key, ip):
    try:
        res: dict = requests.get(
            f"https://api.polsu.xyz/polsu/minecraft/server?key={key}&ip={ip}",
            timeout=10
        ).json()
    except Exception: # polsulpicien wrote this code dont look at me
        # In case the API doesn't respond or reponds with HTML instead of JSON.
        res = {"success": False}
    return res


class Status(commands.Cog):
    def __init__(self, client):
        self.client: commands.Bot = client
        self.key = getenv('API_KEY_POLSU')
        self.ip = 'mc.hypixel.net'


    status_group = app_commands.Group(
        name='status',
        description='Status Group Command'
    )


    @status_group.command(name="hypixel", description="Hypixel's real-time status")
    @app_commands.checks.dynamic_cooldown(generic_command_cooldown)
    async def status_hypixel(self, interaction: discord.Interaction):
        await interaction.response.defer()

        res = await _fetch_server_status(self.key, self.ip)

        if not res["success"]:
            await interaction.followup.send(
                content="Something went while contacting"
                        "`api.polsu.xyz`!\nPlease try again layer",
                ephemeral=True
            )
            return

        data = res["data"]

        format_values = {
            'now': int(time.time()),
            'status': 'Online' if data['online'] else 'Offline',
            'ip': data['ip'],
            'version': data['version'],
            'updated_timestamp': data['time']['last'],
            'ping': f"{data['ping']['last']:,}",
            'max_ping': f"{data['ping']['max']:,}",
            'avg_ping': f"{data['ping']['average']:,}",
            'min_ping': f"{data['ping']['min']:,}",
            'players': f"{data['players']['current']:,}",
            'max_players': f"{data['players']['server_max']:,}",
            'peak_players': f"{data['players']['max']:,}",
            'avg_players': f"{data['players']['average']:,}",
            'min_players': f"{data['players']['min']:,}"
        }
        embeds = load_embeds('status_hypixel', format_values)
        await interaction.followup.send(embeds=embeds)

        update_command_stats(interaction.user.id, 'status_hypixel')


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Status(client))
