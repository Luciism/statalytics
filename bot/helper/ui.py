import os

import shutil
import discord


class SelectModes(discord.ui.Select):
    def __init__(self, user: int, inter: discord.Interaction, mode: str):
        self.user = user
        self.inter = inter
        options = [
            discord.SelectOption(label="Overall"),
            discord.SelectOption(label="Solos"),
            discord.SelectOption(label="Doubles"),
            discord.SelectOption(label="Threes"),
            discord.SelectOption(label="Fours"),
            discord.SelectOption(label="4v4")
            ]
        super().__init__(placeholder=mode.title(), max_values=1, min_values=1, options=options)


    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        mode = self.values[0].lower()

        if interaction.user.id != self.user:
            await interaction.followup.send(
                file=discord.File(f'./database/rendered/{self.inter.id}/{mode}.png'), ephemeral=True)

        else:
            view = ModesView(user=self.user, inter=self.inter, mode=mode)
            await self.inter.edit_original_response(
                attachments=[discord.File(f'./database/rendered/{self.inter.id}/{mode}.png')], view=view)


class ModesView(discord.ui.View):
    def __init__(self, user, inter, mode, *, timeout = 300):
        super().__init__(timeout=timeout)
        self.add_item(SelectModes(user, inter, mode))
        self.inter = inter


    async def on_timeout(self) -> None:
        try:
            self.clear_items()
            await self.inter.edit_original_response(view=self)
        except discord.errors.NotFound:
            pass
        if os.path.isdir(f'./database/rendered/{self.inter.id}'):
            shutil.rmtree(f'./database/rendered/{self.inter.id}')


class LinkButton:
    def __init__(self, label, url, emoji=None) -> None:
        button = discord.ui.Button(label=label, url=url, emoji=emoji)
        self.view = discord.ui.View()
        self.view.add_item(button)
