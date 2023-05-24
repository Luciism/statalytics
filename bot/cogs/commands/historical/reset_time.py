import json
import sqlite3

import discord
from discord import app_commands
from discord.ext import commands

global hours
hours = ['12am', '1am', '2am', '3am', '4am', '5am', '6am', '7am', '8am', '9am', '10am', '11am',
         '12pm', '1pm', '2pm', '3pm', '4pm', '5pm', '6pm', '7pm', '8pm', '9pm', '10pm', '11pm']

class Select(discord.ui.Select):
    def __init__(self, method: str, **kwargs):
        super().__init__(**kwargs, max_values=1, min_values=1)
        self.method = method

    async def callback(self, interaction: discord.Interaction):
        selected_value = int(self.values[0])
        with sqlite3.connect('./database/historical.db') as conn:
            cursor = conn.cursor()
            cursor.execute(f'SELECT timezone FROM configuration WHERE discord_id = {interaction.user.id}')

            if cursor.fetchone():
                cursor.execute(f'UPDATE configuration SET {self.method} = ? WHERE discord_id = ?', (selected_value, interaction.user.id))
            else:
                values = (interaction.user.id, selected_value, 0) if self.method == 'timezone' else (interaction.user.id, 0, selected_value)
                cursor.execute(f'INSERT INTO configuration (discord_id, timezone, reset_hour) VALUES (?, ?, ?)', values)


        if self.method == 'timezone':
            message = f'Successfully updated timezone to `GMT{"+" if selected_value >= 0 else ""}{selected_value}:00`'
        else:
            message = f'Successfully updated reset hour to `{hours[selected_value]}`'
        await interaction.response.send_message(message, ephemeral=True)

class SelectView(discord.ui.View):
    def __init__(self, inter: discord.Interaction, timeout = 300):
        super().__init__(timeout=timeout)
        options = [discord.SelectOption(label=f'GMT{"+" if i-12 >= 0 else ""}{i-12}', value=i-12) for i in reversed(range(25))]
        self.add_item(Select(method='timezone', options=options, placeholder='Select your GMT offset'))
        
        options = [discord.SelectOption(label=hour, value=i) for i, hour in zip(range(24), hours)]
        self.add_item(Select(method='reset_hour', options=options, placeholder='Select the reset hour'))
        self.inter = inter

    async def on_timeout(self) -> None:
        for child in self.children:
            child.disabled = True
        await self.inter.edit_original_response(view=self)

class ResetTime(commands.Cog):
    def __init__(self, client):
        self.client = client

    @app_commands.command(name="resettime", description="Configure the reset timezone for historical stats (GMT)")
    async def reset_time(self, interaction: discord.Interaction):
        with open('./config.json', 'r') as datafile:
            config = json.load(datafile)
        embed_color = int(config['embed_primary_color'], base=16)

        embed = discord.Embed(title='Configure reset time', description="""
        This will determine when your daily, weekly, monthly, and yearly stats roll over.
        GMT offset - your timezone offset to Greenwich Mean Time
        Reset hour - the hour which your historical stats will rollover
        
        Click [here](https://greenwichmeantime.com/current-time/) if you are unsure of your GMT offset.""", color=embed_color)
        await interaction.response.send_message(embed=embed, view=SelectView(inter=interaction), ephemeral=True)

async def setup(client: commands.Bot) -> None:
    await client.add_cog(ResetTime(client))
