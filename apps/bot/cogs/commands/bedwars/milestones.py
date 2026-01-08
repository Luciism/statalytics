import asyncio

import discord
from discord.ext import commands

import helper
import statalib as lib
from statalib.sessions import SessionManager
from render.milestones import render_milestones


class MilestonesCommandCog(commands.Cog):
    @helper.decorators.app_command("milestones")
    @helper.interactions.access_permitted_check()
    async def milestones(
        self,
        interaction: discord.Interaction,
        player: str=None,
        session: int=None
    ) -> None:
        await interaction.response.defer()

        name, uuid = await helper.interactions.fetch_player_info(player, interaction)

        if session == 0:  # Use no session if `0` is specified.
            session_info = None
        else:
            session_info = SessionManager(uuid).get_session(session)

            # Specified session doesn't exist
            if session_info is None and session is not None:
                await interaction.followup.send(
                    f"`{name}` doesn't have an active session with ID: `{session or 1}`!\n" +
                    "Select a valid session or specify `0` in order to not use a session!")
                return

        await interaction.followup.send(lib.config.loading_message())

        skin_model, hypixel_data = await asyncio.gather(
            lib.network.fetch_skin_model(uuid, 128),
            lib.network.fetch_hypixel_data(uuid)
        )

        await helper.interactions.handle_modes_renders(interaction, render_milestones, {
            "name": name,
            "uuid": uuid,
            "session_info": session_info,
            "hypixel_data": hypixel_data,
            "skin_model": skin_model,
            "save_dir": interaction.id
        })


async def setup(client: helper.Client) -> None:
    await client.add_cog(MilestonesCommandCog())
