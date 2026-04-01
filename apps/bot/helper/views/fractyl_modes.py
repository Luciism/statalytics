import io
import typing

import discord
from discord.abc import MISSING # pyright:ignore[reportAny]
from discord.interactions import Interaction

from statalib import Mode, ModesEnum
from statalib.render2 import RenderingClient
from typing_extensions import override

from helper.tips import random_tip_message

from ._custom import CustomBaseView


@typing.final
class FractylModeSelect(discord.ui.Select['FractylModesView']):
    def __init__(
        self,
        interaction_origin: discord.Interaction,
        renderer: RenderingClient,
        modes: list[Mode],
        selected_mode: Mode | None,
        background_img: bytes | None,
    ) -> None:
        self.user_id = interaction_origin.user.id
        self.interaction_origin = interaction_origin
        self.modes = modes
        self.renderer = renderer
        self.background_image = background_img

        selected_mode = selected_mode or modes[0]

        options = [
            discord.SelectOption(label=mode.name, value=mode.id, default=selected_mode == mode)
            for mode in modes
        ]

        super().__init__(
            placeholder="Select a mode",
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
            selected_mode=mode,
            renderer=self.renderer,
            background_img=self.background_image,
            modes=self.modes,
        )

        # Add existing view items
        if self.view:
            for child in self.view.children:
                if not isinstance(child, FractylModeSelect):
                    _ = view.add_item(child)


        _ = await self.interaction_origin.edit_original_response(
            attachments=[file], view=view
        )


class FractylModesView(CustomBaseView):
    def __init__(
        self,
        interaction_origin: discord.Interaction,
        renderer: RenderingClient,
        background_img: bytes | None,
        modes: list[Mode] | None=None,
        selected_mode: Mode | None=None,
        *,
        timeout: int = 300,
    ) -> None:
        if modes is None:
            modes = ModesEnum.non_dream_modes()

        super().__init__(timeout=timeout)
        _ = self.add_item(
            FractylModeSelect(
                interaction_origin, renderer, modes, selected_mode, background_img
            )
        )

        self.background_img: bytes | None = background_img
        self.renderer: RenderingClient = renderer
        self.interaction_origin: Interaction = interaction_origin

    @override
    async def on_timeout(self) -> None:
        try:
            # remove modes dropdown from view
            for child in self.children:
                if isinstance(child, discord.ui.Select):
                    if child.custom_id == "modes_select_item":
                        _ = self.remove_item(child)
                        break

            _ = await self.interaction_origin.edit_original_response(view=self)
        except discord.errors.NotFound:
            pass


    async def send_initial(self, message: str | None=None) -> None:
        img_bytes = await self.renderer.render_to_buffer(self.background_img)

        mode_name = self.renderer.mode.name if self.renderer.mode else "Overall"

        if not message:
            message = random_tip_message(self.interaction_origin.user.id)

        await self.interaction_origin.followup.send(
            content=message or MISSING,
            files=[discord.File(img_bytes, filename=f"{mode_name}.png")],
            view=self
        )

