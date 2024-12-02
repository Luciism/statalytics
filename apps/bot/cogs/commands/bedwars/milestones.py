import asyncio

import discord
from discord import app_commands
from discord.ext import commands

import helper
import statalib as lib
from statalib.sessions import SessionManager
from render.milestones import render_milestones


class Milestones(commands.Cog):
    def __init__(self, client):
        self.client: commands.Bot = client
        self.LOADING_MSG = lib.loading_message()


    @app_commands.command(
        name="milestones",
        description="View the milestone stats of a player")
    @app_commands.describe(
        player='The player you want to view',
        session='The session you want to use (0 for none)')
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.autocomplete(
        player=helper.username_autocompletion,
        session=helper.session_autocompletion)
    @app_commands.checks.dynamic_cooldown(helper.generic_command_cooldown)
    async def milestones(
        self,
        interaction: discord.Interaction,
        player: str=None,
        session: int=None
    ) -> None:
        await interaction.response.defer()
        await helper.interactions.run_interaction_checks(interaction)

        name, uuid = await helper.interactions.fetch_player_info(player, interaction)

        if session == 0:  # Use no session if `0` is specified.
            session_info = None
        else:
            session_info = SessionManager(uuid).get_session(session)

            # Specified session doesn't exist
            if session_info is None and session is not None:
                await interaction.followup.send(
                    f"`{name}` doesn't have an active session with ID: `{session or 1}`!\n"
                    "Select a valid session or specify `0` in order to not use a session!")
                return

        await interaction.followup.send(self.LOADING_MSG)

        skin_model, hypixel_data = await asyncio.gather(
            lib.network.fetch_skin_model(uuid, 128),
            lib.network.fetch_hypixel_data(uuid)
        )

        kwargs = {
            "name": name,
            "uuid": uuid,
            "session_info": session_info,
            "hypixel_data": hypixel_data,
            "skin_model": skin_model,
            "save_dir": interaction.id
        }

        await helper.interactions.handle_modes_renders(interaction, render_milestones, kwargs)
        lib.update_command_stats(interaction.user.id, 'milestones')


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Milestones(client))
