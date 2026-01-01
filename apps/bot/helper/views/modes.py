import os
import shutil
from typing_extensions import override

import discord

from discord.interactions import Interaction
import statalib as lib
from statalib import Mode, ModesEnum

from ._custom import CustomBaseView


class SelectModes(discord.ui.Select):
    def __init__(self, interaction_origin: discord.Interaction, placeholder: str, modes: list[Mode]):
        self.user_id: int = interaction_origin.user.id
        self.interaction_origin: Interaction = interaction_origin
        self.modes: list[Mode] = modes

        options = [discord.SelectOption(label=mode.name, value=mode.id) for mode in modes]

        super().__init__(
            placeholder=placeholder,
            max_values=1,
            min_values=1,
            options=options,
            custom_id='modes_select_item'
        )


    @override
    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()

        selected_mode = self.values[0].lower()
        mode_name = ModesEnum.get_mode_by_id(selected_mode).name or selected_mode

        image = discord.File(
            f'{lib.REL_PATH}/database/rendered/{self.interaction_origin.id}/{selected_mode}.png')

        if interaction.user.id != self.user_id:
            # send seperate image for different user
            await interaction.followup.send(file=image, ephemeral=True)
        else:
            # get updated view (view disappears without)
            view = ModesView(
                interaction_origin=self.interaction_origin, placeholder=mode_name, modes=self.modes)

            # update image and reattach the view
            _ = await self.interaction_origin.edit_original_response(
                attachments=[image], view=view)


class ModesView(CustomBaseView):
    def __init__(
        self,
        interaction_origin: discord.Interaction,
        modes: list[Mode],
        placeholder: str='Select a mode',
        *,
        timeout: int=300
    ) -> None:
        super().__init__(timeout=timeout)
        _ = self.add_item(SelectModes(interaction_origin, placeholder, modes))

        self.interaction_origin: Interaction = interaction_origin


    @override
    async def on_timeout(self) -> None:
        try:
            # remove modes dropdown from view
            for child in self.children:
                if child.custom_id == 'modes_select_item':
                    _ = self.remove_item(child)
                    break

            _ = await self.interaction_origin.edit_original_response(view=self)
        except discord.errors.NotFound:
            pass

        # delete renders
        dir_path = f'{lib.REL_PATH}/database/rendered/{self.interaction_origin.id}'
        if os.path.isdir(dir_path):
            shutil.rmtree(dir_path)
