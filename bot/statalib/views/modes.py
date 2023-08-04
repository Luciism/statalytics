import os
import shutil

import discord

from ..functions import REL_PATH
from ..calctools import real_title_case


class SelectModes(discord.ui.Select):
    def __init__(self, inter: discord.Interaction, mode: str):
        self.user_id = inter.user.id
        self.inter = inter
        options = [
            discord.SelectOption(label="Overall"),
            discord.SelectOption(label="Solos"),
            discord.SelectOption(label="Doubles"),
            discord.SelectOption(label="Threes"),
            discord.SelectOption(label="Fours"),
            discord.SelectOption(label="4v4")
            ]
        super().__init__(
            placeholder=real_title_case(mode),
            max_values=1,
            min_values=1,
            options=options
        )


    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        selected_mode = self.values[0].lower()

        image = discord.File(
            f'{REL_PATH}/database/rendered/{self.inter.id}/{selected_mode}.png')

        if interaction.user.id != self.user_id:
            await interaction.followup.send(file=image, ephemeral=True)
        else:
            view = ModesView(inter=self.inter, mode=selected_mode)
            await self.inter.edit_original_response(attachments=[image], view=view)


class ModesView(discord.ui.View):
    def __init__(self, inter, mode, *, timeout = 300):
        super().__init__(timeout=timeout)
        self.add_item(SelectModes(inter, mode))
        self.inter = inter


    async def on_timeout(self) -> None:
        try:
            self.clear_items()
            await self.inter.edit_original_response(view=self)
        except discord.errors.NotFound:
            pass
        if os.path.isdir(f'{REL_PATH}/database/rendered/{self.inter.id}'):
            shutil.rmtree(f'{REL_PATH}/database/rendered/{self.inter.id}')