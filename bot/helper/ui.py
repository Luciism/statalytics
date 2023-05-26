import os
import sqlite3
from json import load as load_json

import shutil
import discord
from helper.functions import start_session

class SubmitSuggestion(discord.ui.Modal, title='Submit Suggestion'):
    def __init__(self, channel, **kwargs):
        self.channel = channel
        super().__init__(**kwargs)

    suggestion = discord.ui.TextInput(label='Suggestion:', placeholder='You should add...', style=discord.TextStyle.long)

    async def on_submit(self, interaction: discord.Interaction):
        with open('./config.json', 'r') as datafile:
            config = load_json(datafile)
        embed_color = int(config['embed_primary_color'], base=16)
        submit_embed = discord.Embed(title=f'Suggestion by {interaction.user} ({interaction.user.id})', description=f'**Suggestion:**\n{self.suggestion}', color=embed_color)

        await self.channel.send(embed=submit_embed)
        await interaction.response.send_message('Successfully submitted suggestion!', ephemeral=True)

class ManageSession(discord.ui.View):
    def __init__(self, session: int, uuid: str, method: str) -> None:
        super().__init__(timeout = 20)
        self.method = method
        self.session = session
        self.uuid = uuid

    async def on_timeout(self) -> None:
        for item in self.children:
            item.disabled = True
        await self.message.edit(view=self)

    @discord.ui.button(label = "Confirm", style = discord.ButtonStyle.danger, custom_id = "confirm")
    async def delete(self, interaction: discord.Interaction, button: discord.ui.Button):
        button.disabled = True
        await self.message.edit(view=self)
        await interaction.response.defer()
        with sqlite3.connect('./database/sessions.db') as conn:
            cursor = conn.cursor()
            if self.method == "delete":
                cursor.execute("DELETE FROM sessions WHERE session = ? AND uuid = ?", (self.session, self.uuid))
                message = f'Session `{self.session}` has been deleted successfully!'
            else:
                cursor.execute("DELETE FROM sessions WHERE session = ? AND uuid = ?", (self.session, self.uuid))
        if self.method != "delete":
            start_session(self.uuid, self.session)
            message = f'Session `{self.session}` has been reset successfully!'
        await interaction.followup.send(message, ephemeral=True)

# ------------------------------------------------------------------------------------------ #
class Select(discord.ui.Select):
    def __init__(self, user, inter, mode):
        self.user = user
        self.inter = inter
        self.mode = f'{mode[0].upper()}{mode[1:]}'
        options=[
            discord.SelectOption(label="Overall"),
            discord.SelectOption(label="Solos"),
            discord.SelectOption(label="Doubles"),
            discord.SelectOption(label="Threes"),
            discord.SelectOption(label="Fours"),
            discord.SelectOption(label="4v4")
            ]
        super().__init__(placeholder=self.mode, max_values=1, min_values=1, options=options)
    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        mode = self.values[0].lower()
        if not interaction.user.id == self.user:
            await interaction.followup.send(file=discord.File(f'./database/activerenders/{self.inter.id}/{mode}.png'),ephemeral=True)
        else:
            view = SelectView(user=self.user, inter=self.inter, mode=mode)
            await self.inter.edit_original_response(attachments=[discord.File(f'./database/activerenders/{self.inter.id}/{mode}.png')], view=view)

class SelectView(discord.ui.View):
    def __init__(self, user, inter, mode, *, timeout = 300):
        super().__init__(timeout=timeout)
        self.add_item(Select(user, inter, mode))
        self.inter = inter

    async def on_timeout(self) -> None:
        self.clear_items()
        await self.inter.edit_original_response(view=self)
        if os.path.isdir(f'./database/activerenders/{self.inter.id}'):
            shutil.rmtree(f'./database/activerenders/{self.inter.id}')
