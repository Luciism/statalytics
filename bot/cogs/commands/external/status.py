# api.polsu.xyz

import time
from os import getenv

import discord
from discord import app_commands
from discord.ext import commands
from aiohttp import ClientSession

import statalib as lib


async def _fetch_server_status(api_key: str, ip: str):
    try:
        options = {
            'url': f"https://api.polsu.xyz/polsu/minecraft/server?ip={ip}",
            'headers': {'Api-Key': api_key},
            'timeout': 10
        }
        async with ClientSession() as session:
            res = await session.get(**options)
            data = await res.json()
    except Exception:  # polsulpicien wrote this code dont look at me
        # In case the API doesn't respond or reponds with HTML instead of JSON.
        data = {"success": False}
    return data


class StatusData:
    def __init__(self, data: dict) -> None:
        self.now: int = int(time.time())
        self.updated_timestamp: int = data['time']['last']

        self.ip: str = data['ip']
        self.status: str = 'Online' if data['online'] else 'Offline'
        self.version: str = data['version']

        self.ping: str = f"{data['ping']['last']:,}"
        self.max_ping: str = f"{data['ping']['max']:,}"
        self.avg_ping: str = f"{data['ping']['average']:,}"
        self.min_ping: str = f"{data['ping']['min']:,}"

        self.players: str = f"{data['players']['current']:,}"
        self.max_players: str = f"{data['players']['server_max']:,}"
        self.peak_players: str = f"{data['players']['max']:,}"
        self.avg_players: str = f"{data['players']['average']:,}"
        self.min_players: str = f"{data['players']['min']:,}"


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
    @app_commands.checks.dynamic_cooldown(lib.generic_command_cooldown)
    async def status_hypixel(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await lib.run_interaction_checks(interaction)

        res = await _fetch_server_status(self.key, self.ip)

        if not res["success"]:
            await interaction.followup.send(
                content="Something went wrong while contacting"
                        "`api.polsu.xyz`!\nPlease try again later.",
                ephemeral=True
            )
            return

        data = res["data"]
        d = StatusData(data)

        embeds = [
            {
                "title": "Hypixel Status",
                "description": f"""
                    Hypixel's current server information.

                    **` > ` Status**: `{d.status}`
                    **` > ` IP**: **`{d.ip}`**
                    **` > ` Version**: `{d.version}`

                    **` > ` Updated**: <t:{d.updated_timestamp}>
                """.replace('\t', ''),
                "footer": {
                    "text": "Powered by api.polsu.xyz"
                },
                "thumbnail": {
                    "url":
                        f"https://assets.polsu.xyz/minecraft/server/icon/{d.ip}.png?t={d.now}"
                },
                "image": {
                    "url":
                        f"https://assets.polsu.xyz/minecraft/server/motd/{d.ip}.png?t={d.now}"
                },
                "color": 3092790
            },
            {
                "title": "Ping",
                "description": f"""
                    **` > ` Ping**: `{d.ping}`

                    **` > ` Max**: `{d.max_ping}`
                    **` > ` Average**: `{d.avg_ping}`
                    **` > ` Min**: `{d.min_ping}`
                """.replace('\t', ''),
                "footer": {
                    "text": "UTC Time  -  Ping in ms (USA - Los Angeles)"
                },
                "image": {
                    "url":
                        f"https://assets.polsu.xyz/minecraft/server/ping/{d.ip}.png?t={d.now}"
                },
                "color": 3092790
            },
            {
                "title": "Players",
                "description": f"""
                    **` > ` Players**: `{d.players} / {d.max_players}`

                    **` > ` Peak**: `{d.peak_players}`
                    **` > ` Average**: `{d.avg_players}`
                    **` > ` Min**: `{d.min_players}`
                """.replace('\t', ''),
                "footer": {
                    "text": "Hypixel Status"
                },
                "image": {
                    "url":
                        f"https://assets.polsu.xyz/minecraft/server/players/{d.ip}.png?t={d.now}"
                },
                "color": 3092790
            }
        ]

        embeds = [discord.Embed.from_dict(embed) for embed in embeds]
        await interaction.followup.send(embeds=embeds)

        lib.update_command_stats(interaction.user.id, 'status_hypixel')


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Status(client))
