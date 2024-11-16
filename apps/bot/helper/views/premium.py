import discord

import statalib as lib


def _premium_info_button(label: str, package: str) -> discord.ui.Button:
    btn = discord.ui.Button(
        label=label,
        custom_id=f"premium_info:{package}_button"
    )
    async def callback(interaction: discord.Interaction) -> None:
        await interaction.response.send_message(
            embeds=lib.load_embeds(f"premium/{package}", color="primary"))
    btn.callback = callback

    return btn


class PremiumInfoView(lib.shared_views.CustomBaseView):
    def __init__(self) -> None:
        super().__init__(timeout=None)
        self.add_item(_premium_info_button("Pro", package="pro"))
        self.add_item(_premium_info_button("Basic", package="basic"))