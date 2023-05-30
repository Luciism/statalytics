import sqlite3
from json import load as load_json

import discord
from discord import app_commands
from discord.ext import commands

from mcuuid import MCUUID
from helper.functions import link_account, update_command_stats


class Linking(commands.Cog):
    def __init__(self, client):
        self.client: discord.Client = client
        self.GENERATING_MESSAGE = 'Generating please wait <a:loading1:1062561739989860462>'


    @app_commands.command(name = "link", description = "Link your account")
    @app_commands.describe(username='The player you want to link to')
    async def link(self, interaction: discord.Interaction, username: str):
        try:
            uuid = MCUUID(name=username).uuid
            name = MCUUID(name=username).name
        except Exception:
            await interaction.response.send_message("That player does not exist!")
            return

        # Linking Logic
        response = link_account(str(interaction.user), interaction.user.id, name, uuid)
        refined = name.replace('_', r'\_')
        if response is True: await interaction.response.send_message(f"Successfully linked to **{refined}** ({interaction.user})")
        # If discord isnt connected to hypixel
        else:
            await interaction.response.defer()
            with open('./config.json', 'r') as datafile:
                config = load_json(datafile)
            embed_color = int(config['embed_primary_color'], base=16)
            if response is None:
                embed = discord.Embed(title=f"{refined}'s discord isn't connected on hypixel!", description='Example of how to connect your discord to hypixel:', color=embed_color)
            else:
                embed = discord.Embed(title="How to connect discord to hypixel", description=f'''That player is connected to a different discord tag on hypixel!
                            If you own the **{refined}** account, you must __update your hypixel connection__ to match your current discord tag:''', color=embed_color)
            embed.set_image(url='https://cdn.discordapp.com/attachments/1027817138095915068/1061647399266811985/result.gif')
            await interaction.followup.send(embed=embed)

        update_command_stats(interaction.user.id, 'link')


    @app_commands.command(name = "unlink", description = "Unlink your account")
    async def unlink(self, interaction: discord.Interaction):
        with sqlite3.connect('./database/linked_accounts.db') as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM linked_accounts WHERE discord_id = {interaction.user.id}")
            if cursor.fetchone():
                cursor.execute(f"DELETE FROM linked_accounts WHERE discord_id = {interaction.user.id}")
                message = 'Successfully unlinked your account!'
            else: message = "You don't have an account linked! In order to link use `/link`!"
            await interaction.response.send_message(message)

        update_command_stats(interaction.user.id, 'unlink')


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Linking(client))
