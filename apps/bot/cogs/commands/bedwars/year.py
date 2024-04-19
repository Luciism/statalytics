import asyncio

import discord
from discord import app_commands
from discord.ext import commands

import statalib as lib
from render.year import render_year


class Year(commands.Cog):
    def __init__(self, client):
        self.client: commands.Bot = client
        self.LOADING_MSG = lib.loading_message()


    year_group = app_commands.Group(
        name='year',
        description='View the a players projected stats for a future year'
    )


    async def year_command(
        self,
        interaction: discord.Interaction,
        name: str,
        uuid: str,
        session: int,
        year: int
    ):
        await lib.run_interaction_checks(interaction)
        await interaction.followup.send(self.LOADING_MSG)

        skin_model, hypixel_data = await asyncio.gather(
            lib.fetch_skin_model(uuid, 144),
            lib.fetch_hypixel_data(uuid)
        )

        session = await lib.find_dynamic_session_interaction(
            interaction_response=interaction.edit_original_response,
            username=name,
            uuid=uuid,
            hypixel_data=hypixel_data,
            session=session
        )

        kwargs = {
            "name": name,
            "uuid": uuid,
            "session": session,
            "year": year,
            "hypixel_data": hypixel_data,
            "skin_model": skin_model,
            "save_dir": interaction.id
        }

        await lib.handle_modes_renders(interaction, render_year, kwargs)
        lib.update_command_stats(interaction.user.id, f'year_{year}')


    @year_group.command(
        name="2025",
        description="View the a players projected stats for 2025")
    @app_commands.describe(
        player='The player you want to view',
        session='The session you want to use')
    @app_commands.autocomplete(
        player=lib.username_autocompletion,
        session=lib.session_autocompletion)
    @app_commands.checks.dynamic_cooldown(lib.generic_command_cooldown)
    async def year_2025(self, interaction: discord.Interaction,
                        player: str=None, session: int=None):
        await interaction.response.defer()
        name, uuid = await lib.fetch_player_info(player, interaction)
        await self.year_command(interaction, name, uuid, session, 2025)


    @year_group.command(
        name="2026",
        description="View the a players projected stats for 2026")
    @app_commands.describe(
        player='The player you want to view',
        session='The session you want to use')
    @app_commands.autocomplete(
        player=lib.username_autocompletion,
        session=lib.session_autocompletion)
    @app_commands.checks.dynamic_cooldown(lib.generic_command_cooldown)
    async def year_2026(self, interaction: discord.Interaction,
                        player: str=None, session: int=None):
        await interaction.response.defer()
        name, uuid = await lib.fetch_player_info(player, interaction)

        discord_id = lib.uuid_to_discord_id(uuid)

        # Either command user or checked player has access
        condition_1 = lib.has_access(discord_id, 'year_2026')
        condition_2 = lib.has_access(interaction.user.id, 'year_2026')

        if not condition_1 and not condition_2:
            embeds = lib.load_embeds('2026', color='primary')
            await interaction.followup.send(embeds=embeds)
            return

        await self.year_command(interaction, name, uuid, session, 2026)


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Year(client))
