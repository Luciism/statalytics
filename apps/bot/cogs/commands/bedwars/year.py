import asyncio

import discord
from discord import app_commands
from discord.ext import commands

import helper
import statalib as lib
from statalib.accounts import Account
from render.year import render_year


class Year(commands.Cog):
    def __init__(self, client):
        self.client: commands.Bot = client
        self.LOADING_MSG = lib.config.loading_message()


    year_group = app_commands.Group(
        name='year',
        description='View the a players projected stats for a future year',
        allowed_contexts=app_commands.AppCommandContext(
            guild=True, dm_channel=True, private_channel=True),
        allowed_installs=app_commands.AppInstallationType(guild=True, user=True)
    )


    async def year_command(
        self,
        interaction: discord.Interaction,
        name: str,
        uuid: str,
        session: int,
        year: int
    ) -> None:
        await helper.interactions.run_interaction_checks(interaction)
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

        kwargs = {
            "name": name,
            "uuid": uuid,
            "session_info": session_info,
            "year": year,
            "hypixel_data": hypixel_data,
            "skin_model": skin_model,
            "save_dir": interaction.id
        }

        await helper.interactions.handle_modes_renders(interaction, render_year, kwargs)
        lib.usage.update_command_stats(interaction.user.id, f'year_{year}')


    @year_group.command(
        name="2025",
        description="View the a players projected stats for 2025")
    @app_commands.describe(
        player='The player you want to view',
        session='The session you want to use')
    @app_commands.autocomplete(
        player=helper.username_autocompletion,
        session=helper.session_autocompletion)
    @app_commands.checks.dynamic_cooldown(helper.generic_command_cooldown)
    async def year_2025(
        self, interaction: discord.Interaction, player: str=None, session: int=None
    ) -> None:
        await interaction.response.defer()
        name, uuid = await helper.interactions.fetch_player_info(player, interaction)
        await self.year_command(interaction, name, uuid, session, 2025)


    @year_group.command(
        name="2026",
        description="View the a players projected stats for 2026")
    @app_commands.describe(
        player='The player you want to view',
        session='The session you want to use')
    @app_commands.autocomplete(
        player=helper.username_autocompletion,
        session=helper.session_autocompletion)
    @app_commands.checks.dynamic_cooldown(helper.generic_command_cooldown)
    async def year_2026(
        self, interaction: discord.Interaction, player: str=None, session: int=None
    ) -> None:
        await interaction.response.defer()
        name, uuid = await helper.interactions.fetch_player_info(player, interaction)

        discord_id = lib.accounts.uuid_to_discord_id(uuid)

        # Either command user or checked player has access
        condition_1 = Account(discord_id).permissions.has_access('year_2026')
        condition_2 = Account(interaction.user.id).permissions.has_access('year_2026')

        if not condition_1 and not condition_2:
            embed = lib.Embeds.problems.no_premium_2026()
            await interaction.followup.send(embed=embed)
            return

        await self.year_command(interaction, name, uuid, session, 2026)


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Year(client))
