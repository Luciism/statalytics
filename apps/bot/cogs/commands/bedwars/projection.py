import asyncio

import discord
from discord import app_commands
from discord.ext import commands

import statalib as lib
import helper
from render.projection import render_projection


class Projection(commands.Cog):
    def __init__(self, client):
        self.client: commands.Bot = client
        self.LOADING_MSG = lib.loading_message()


    @app_commands.command(
        name="prestige",
        description="View the projected stats of a player")
    @app_commands.describe(
        player='The player you want to view',
        prestige='The prestige you want to view',
        session='The session you want to use as a benchmark (defaults to 1)')
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.autocomplete(
        player=helper.username_autocompletion,
        session=helper.session_autocompletion)
    @app_commands.checks.dynamic_cooldown(helper.generic_command_cooldown)
    async def projected_stats(
        self,
        interaction: discord.Interaction,
        prestige: int=None,
        player: str=None,
        session: int=None
    ) -> None:
        await interaction.response.defer()
        await helper.interactions.run_interaction_checks(interaction)

        name, uuid = await helper.interactions.fetch_player_info(player, interaction)

        await interaction.followup.send(self.LOADING_MSG)

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

        kwargs = {
            "name": name,
            "uuid": uuid,
            "session_info": session_info,
            "target": prestige,
            "hypixel_data": hypixel_data,
            "skin_model": skin_model,
            "save_dir": interaction.id
        }

        await helper.interactions.handle_modes_renders(interaction, render_projection, kwargs)
        lib.update_command_stats(interaction.user.id, 'projection')


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Projection(client))
