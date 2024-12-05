import json

import discord
from discord.ext import commands

import statalib as lib


class Growth(commands.Cog):
    def __init__(self, client):
        self.client: commands.Bot = client


    def update_server_count_file(self):
        with open(f'{lib.REL_PATH}/database/server_count.json', 'w') as datafile:
            json.dump({'server_count': len(self.client.guilds)}, datafile, indent=4)


    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        lib.usage.insert_growth_data(guild.id, action='add', growth='guild')
        self.update_server_count_file()


    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild):
        lib.usage.insert_growth_data(guild.id, action='remove', growth='guild')
        self.update_server_count_file()


    @commands.Cog.listener()
    async def on_ready(self) -> None:
        self.update_server_count_file()


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Growth(client))
