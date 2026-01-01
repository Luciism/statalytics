import discord

from ._custom import CustomBaseView
from ..embeds import Embeds

def _premium_info_button(label: str, package: str) -> discord.ui.Button:
    btn = discord.ui.Button(
        label=label,
        custom_id=f"premium_info:{package}_button"
    )

    if package == "pro":
        embed = Embeds.premium.pro()
    else:
        embed = Embeds.premium.basic()

    async def callback(interaction: discord.Interaction) -> None:
        await interaction.response.send_message(embed=embed)
    btn.callback = callback

    return btn


class PremiumInfoView(CustomBaseView):
    def __init__(self) -> None:
        super().__init__(timeout=None)
        _ = self.add_item(_premium_info_button("Pro", package="pro"))
        _ = self.add_item(_premium_info_button("Basic", package="basic"))
