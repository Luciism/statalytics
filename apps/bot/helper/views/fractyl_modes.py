import io
import os
import shutil
import typing

import discord
import statalib as lib
from discord.interactions import Interaction
from statalib import Mode, ModesEnum
from statalib.render2 import RenderingClient
from typing_extensions import override

from ._custom import CustomBaseView


@typing.final
class FractylModeSelect(discord.ui.Select[typing.Any]):
    def __init__(
        self,
        interaction_origin: discord.Interaction,
        placeholder: str,
        renderer: RenderingClient,
        background_img: bytes | None,
        modes: list[Mode],
    ) -> None:
        self.user_id = interaction_origin.user.id
        self.interaction_origin = interaction_origin
        self.modes = modes
        self.renderer = renderer
        self.background_image = background_img

        options = [
            discord.SelectOption(label=mode.name, value=mode.id) for mode in modes
        ]

        super().__init__(
            placeholder=placeholder,
            max_values=1,
            min_values=1,
            options=options,
            custom_id="modes_select_item",
        )

    @override
    async def callback(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()

        selected_mode = self.values[0].lower()
        mode = ModesEnum.get_mode_by_id(selected_mode) or None

        if mode is None:
            return  # mode not found

        self.renderer.mode = mode
        image = await self.renderer.render(self.background_image)

        img_buf = io.BytesIO(image)
        _ = img_buf.seek(0)

        file = discord.File(img_buf, filename=f"render-{selected_mode}.png")

        if interaction.user.id != self.user_id:
            # send seperate image for different user
            await interaction.followup.send(file=file, ephemeral=True)
            return

        # Get updated view (view disappears without).
        view = FractylModesView(
            interaction_origin=self.interaction_origin,
            placeholder=mode.name,
            renderer=self.renderer,
            background_img=self.background_image,
            modes=self.modes,
        )

        _ = await self.interaction_origin.edit_original_response(
            attachments=[file], view=view
        )


class FractylModesView(CustomBaseView):
    def __init__(
        self,
        interaction_origin: discord.Interaction,
        renderer: RenderingClient,
        background_img: bytes | None,
        modes: list[Mode],
        placeholder: str = "Select a mode",
        *,
        timeout: int = 300,
    ) -> None:
        super().__init__(timeout=timeout)
        _ = self.add_item(
            FractylModeSelect(
                interaction_origin, placeholder, renderer, background_img, modes
            )
        )

        self.interaction_origin: Interaction = interaction_origin

    @override
    async def on_timeout(self) -> None:
        try:
            # remove modes dropdown from view
            for child in self.children:
                if child.custom_id == "modes_select_item":
                    _ = self.remove_item(child)
                    break

            _ = await self.interaction_origin.edit_original_response(view=self)
        except discord.errors.NotFound:
            pass

        # delete renders
        dir_path = f"{lib.REL_PATH}/database/rendered/{self.interaction_origin.id}"
        if os.path.isdir(dir_path):
            shutil.rmtree(dir_path)

