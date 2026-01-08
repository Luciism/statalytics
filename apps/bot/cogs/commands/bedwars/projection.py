import asyncio

import discord
from discord.ext import commands

import statalib as lib
import helper
from render.projection import render_projection


class ProjectionCommandCog(commands.Cog):
    @helper.decorators.app_command("projection")
    @helper.interactions.access_permitted_check()
    async def projected_stats(
        self,
        interaction: discord.Interaction,
        prestige: int=None,
        player: str=None,
        session: int=None
    ) -> None:
        await interaction.response.defer()

        name, uuid = await helper.interactions.fetch_player_info(player, interaction)

        await interaction.followup.send(lib.config.loading_message())

        skin_model, hypixel_data = await asyncio.gather(
            lib.network.fetch_skin_model(uuid, 144),
            lib.network.fetch_hypixel_data(uuid)
        )

        session_info = await helper.interactions.find_dynamic_session_interaction(
            interaction_callback=interaction.edit_original_response,
            username=name,
            uuid=uuid,
            hypixel_data=hypixel_data,
            session=session
        )

        if not prestige:
            if hypixel_data.get('player'):
                current_star = hypixel_data.get(
                    'player', {}).get('achievements', {}).get('bedwars_level', 0)
            else:
                current_star = 0
            prestige = (current_star // 100 + 1) * 100

        prestige = max(prestige, 1)  # 1 or higher

        await helper.interactions.handle_modes_renders(interaction, render_projection, {
            "name": name,
            "uuid": uuid,
            "session_info": session_info,
            "target": prestige,
            "hypixel_data": hypixel_data,
            "skin_model": skin_model,
            "save_dir": interaction.id
        })


async def setup(client: helper.Client) -> None:
    await client.add_cog(ProjectionCommandCog())
