import json
import time
import sqlite3
from typing import Literal

import discord
from discord.ext import commands


def insert_growth_data(
    discord_id: int,
    action: Literal['add', 'remove'],
    growth: Literal['guild', 'user'],
    timestamp: float=None
):
    """
    Inserts a row of growth data into database
    :param discord_id: the respective discord id of the event (guild, user, etc)
    :param action: the action that caused growth (add, remove, etc)
    :param growth: what impacted the growth (guild, user, etc)
    :param timestamp: the timestamp of the action (defaults to now)
    """
    if timestamp is None:
        timestamp = time.time()

    with sqlite3.connect('./database/core.db') as conn:
        cursor = conn.cursor()

        cursor.execute(
            'INSERT INTO growth_data '
            '(timestamp, discord_id, action, growth) '
            'VALUES (?, ?, ?, ?)',
            (timestamp, discord_id, action, growth)
        )


class Growth(commands.Cog):
    def __init__(self, client):
        self.client: discord.Client = client


    def update_server_count_file(self):
        with open('./database/server_count.json', 'w') as datafile:
            json.dump({'server_count': len(self.client.guilds)}, datafile, indent=4)


    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        insert_growth_data(guild.id, action='add', growth='guild')
        self.update_server_count_file()


    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild):
        insert_growth_data(guild.id, action='remove', growth='guild')
        self.update_server_count_file()


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Growth(client))
