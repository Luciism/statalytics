import os
import shutil

import discord

from ..common import REL_PATH
from ..calctools import real_title_case
from .custom import CustomBaseView


class SelectModes(discord.ui.Select):
    def __init__(self, interaction_origin: discord.Interaction, placeholder: str):
        self.user_id = interaction_origin.user.id
        self.interaction_origin = interaction_origin
        options = [
            discord.SelectOption(label="Overall"),
            discord.SelectOption(label="Solos"),
            discord.SelectOption(label="Doubles"),
            discord.SelectOption(label="Threes"),
            discord.SelectOption(label="Fours"),
            discord.SelectOption(label="4v4")
            ]
        super().__init__(
            placeholder=real_title_case(placeholder),
            max_values=1,
            min_values=1,
            options=options,
            custom_id='modes_select_item'
        )


    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()

        selected_mode = self.values[0].lower()

        image = discord.File(
            f'{REL_PATH}/database/rendered/{self.interaction_origin.id}/{selected_mode}.png')

        if interaction.user.id != self.user_id:
            # send seperate image for different user
            await interaction.followup.send(file=image, ephemeral=True)
        else:
            # get updated view (view disappears without)
            view = ModesView(
                interaction_origin=self.interaction_origin, placeholder=selected_mode)

            # update image and reattach the view
            await self.interaction_origin.edit_original_response(
                attachments=[image], view=view)


class ModesView(CustomBaseView):
    def __init__(
        self,
        interaction_origin: discord.Interaction,
        placeholder: str='Select a mode',
        *,
        timeout=300
    ) -> None:
        super().__init__(timeout=timeout)
        self.add_item(SelectModes(interaction_origin, placeholder))

        self.interaction_origin = interaction_origin


    async def on_timeout(self) -> None:
        try:
            # remove modes dropdown from view
            for child in self.children:
                if child.custom_id == 'modes_select_item':
                    self.remove_item(child)
                    break

            await self.interaction_origin.edit_original_response(view=self)
        except discord.errors.NotFound:
            pass

        # delete renders
        dir_path = f'{REL_PATH}/database/rendered/{self.interaction_origin.id}'
        if os.path.isdir(dir_path):
            shutil.rmtree(dir_path)
