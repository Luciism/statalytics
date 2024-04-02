import asyncio

import discord
from discord import app_commands
from discord.ext import commands

import statalib as lib
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
    @app_commands.autocomplete(
        player=lib.username_autocompletion,
        session=lib.session_autocompletion)
    @app_commands.checks.dynamic_cooldown(lib.generic_command_cooldown)
    async def milestones(self, interaction: discord.Interaction,
                         player: str=None, session: int=None):
        await interaction.response.defer()
        await lib.run_interaction_checks(interaction)

        name, uuid = await lib.fetch_player_info(player, interaction)

        # check if session if valid only if a session is being used
        if session == 0:
            valid_session = 0
        else:
            valid_session = lib.find_dynamic_session(uuid, session)

        # session is not specified and none are found, so use no session
        if session is None and valid_session is None:
            valid_session = 0
        # specified session doesnt exist
        elif valid_session is None:
            await interaction.followup.send(
                f"`{name}` doesn't have an active session with ID: `{session or 1}`!\n"
                "Select a valid session or specify `0` in order to not use a session!")
            return

        await interaction.followup.send(self.LOADING_MSG)

        skin_model, hypixel_data = await asyncio.gather(
            lib.fetch_skin_model(uuid, 128),
            lib.fetch_hypixel_data(uuid)
        )

        kwargs = {
            "name": name,
            "uuid": uuid,
            "session": valid_session,
            "hypixel_data": hypixel_data,
            "skin_model": skin_model,
            "save_dir": interaction.id
        }

        await lib.handle_modes_renders(interaction, render_milestones, kwargs)
        lib.update_command_stats(interaction.user.id, 'milestones')


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Milestones(client))
