import asyncio
from typing import final
from typing_extensions import override
import discord
from discord.ext import commands

import statalib as lib
from statalib import render2
from calc.cosmetics import ActiveCosmetics
import helper


@final
class ActiveCosmeticsRenderer(render2.RenderingClient):
    def __init__(
        self,
        skin_model_bytes: bytes,
        username: str,
        data: lib.HypixelData,
    ) -> None:
        super().__init__(route="active-cosmetics")

        self._skin_model_bytes = skin_model_bytes
        self._username = username
        self._data = data


    @override
    def placeholder_values(self) -> render2.PlaceholderValues:
        cosmetics = ActiveCosmetics(self._username, self._data)

        text_placeholders = {
            "cosmetic_spray#text": cosmetics.spray,
            "cosmetic_glyph#text": cosmetics.glyph,
            "cosmetic_shopkeeper_skin#text": cosmetics.shopkeeper_skin,
            "cosmetic_projectile_trail#text": cosmetics.projectile_trail,
            "cosmetic_death_cry#text": cosmetics.death_cry,
            "cosmetic_wood_skin#text": cosmetics.wood_skin,
            "cosmetic_final_kill_effect#text": cosmetics.kill_effect,
            "cosmetic_island_topper#text": cosmetics.island_topper,
            "cosmetic_victory_dance#text": cosmetics.victory_dance,
            "cosmetic_bed_destroy#text": cosmetics.bed_destroy,
            "cosmetic_kill_message#text": cosmetics.kill_message,
            "total_cosmetics_owned#text": f"{cosmetics.total_cosmetics_owned:,}",
        }

        placeholder_values = render2.PlaceholderValues.new(text=text_placeholders)
        placeholder_values.add_skin_model(self._skin_model_bytes)
        placeholder_values.add_footer_text()
        placeholder_values.add_current_level(int(cosmetics.level))
        placeholder_values.add_playername(cosmetics.get_rank_info())

        return placeholder_values


class CosmeticsCommandCog(commands.Cog):
    @helper.decorators.app_command("cosmetics")
    @helper.interactions.access_permitted_check()
    async def active_cosmetics(
        self,
        interaction: discord.Interaction,
        player: str | None=None
    ):
        await interaction.response.defer()

        name, uuid = await helper.interactions.fetch_player_info(player, interaction)

        hypixel_data, skin_model = await asyncio.gather(
            lib.network.fetch_hypixel_data(uuid),
            lib.network.fetch_skin_model(uuid)
        )

        renderer = ActiveCosmeticsRenderer(skin_model, name, hypixel_data)
        background_img = renderer.bg(interaction.user.id, "cosmetics", uuid)
        img_bytes = await renderer.render_to_buffer(background_img)
        
        await interaction.followup.send(
            content=helper.random_tip_message(interaction.user.id),
            files=[discord.File(img_bytes, filename="cosmetics.png")],
        )



async def setup(client: helper.Client) -> None:
    await client.add_cog(CosmeticsCommandCog())
