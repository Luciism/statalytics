import os
import shutil
import sqlite3
import discord
import reqapi

class DeleteSession(discord.ui.View):
    def __init__(self, session, uuid, method) -> None:
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
        with sqlite3.connect(f'{os.getcwd()}/database/sessions.db') as conn:
            cursor = conn.cursor()
            if self.method == "delete":
                cursor.execute("DELETE FROM sessions WHERE session = ? AND uuid = ?", (self.session, self.uuid))
                await interaction.followup.send(f'{interaction.user.mention} Successfully deleted session {self.session}!')
                conn.commit()
            else:
                cursor.execute("DELETE FROM sessions WHERE session = ? AND uuid = ?", (self.session, self.uuid))
                conn.commit()
        if self.method != "delete":
            reqapi.startsession(self.uuid, self.session)
            await interaction.followup.send(f'{interaction.user.mention} Successfully reset session {self.session}!')

# ------------------------------------------------------------------------------------------ #
class Select(discord.ui.Select):
    def __init__(self, name, user, interid, inter, mode):
        self.name = name
        self.user = user
        self.interid = interid
        self.inter = inter
        self.mode = f'{mode[0].upper()}{mode[1:]}'
        options=[
            discord.SelectOption(label="Overall"),
            discord.SelectOption(label="Solos"),
            discord.SelectOption(label="Doubles"),
            discord.SelectOption(label="Threes"),
            discord.SelectOption(label="Fours")
            ]
        super().__init__(placeholder=self.mode,max_values=1,min_values=1,options=options)
    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        mode = self.values[0].lower()
        if not interaction.user.id == self.user:
            await interaction.followup.send(file=discord.File(f'{os.getcwd()}/database/activerenders/{self.interid.id}/{mode}.png'),ephemeral=True)
        else:
            view = SelectView(self.name, user=self.user, interid=self.interid, inter=self.inter, mode=mode)
            await self.inter.edit_original_response(attachments=[discord.File(f'{os.getcwd()}/database/activerenders/{self.interid.id}/{mode}.png')], view=view)

class SelectView(discord.ui.View):
    def __init__(self, name, user, interid, inter, mode, *, timeout = 300):
        super().__init__(timeout=timeout)
        self.add_item(Select(name, user, interid, inter, mode))
        self.interid = interid
        self.inter = inter

    async def on_timeout(self) -> None:
        self.clear_items()
        await self.inter.edit_original_response(view=self)
        if os.path.isdir(f'{os.getcwd()}/database/activerenders/{self.interid.id}'):
            print(f'{self.interid.id} timed out... deleting directory!')
            shutil.rmtree(f'{os.getcwd()}/database/activerenders/{self.interid.id}')
