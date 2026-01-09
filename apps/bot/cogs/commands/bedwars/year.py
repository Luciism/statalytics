import asyncio
from datetime import UTC, datetime

import discord
import statalib as lib
from discord import app_commands
from discord.ext import commands
from statalib.accounts import Account

import helper
from render.year import render_year


class YearCommandCog(commands.Cog):
    year_group: app_commands.Group = app_commands.Group(
        name="year",
        description="View the a players projected stats for a future year",
        allowed_contexts=app_commands.AppCommandContext(
            guild=True, dm_channel=True, private_channel=True
        ),
        allowed_installs=app_commands.AppInstallationType(guild=True, user=True),
    )

    async def year_command(
        self,
        interaction: discord.Interaction,
        name: str,
        uuid: str,
        session: int | None,
        year: int,
    ) -> None:
        await interaction.followup.send(lib.config.loading_message())

        skin_model, hypixel_data = await asyncio.gather(
            lib.network.fetch_skin_model(uuid, 144),
            lib.network.fetch_hypixel_data(uuid),
        )

        session_info = await helper.interactions.find_dynamic_session_interaction(
            interaction_callback=interaction.edit_original_response,
            username=name,
            uuid=uuid,
            hypixel_data=hypixel_data,
            session=session,
        )

        await helper.interactions.handle_modes_renders(
            interaction,
            render_year,
            {
                "name": name,
                "uuid": uuid,
                "session_info": session_info,
                "year": year,
                "hypixel_data": hypixel_data,
                "skin_model": skin_model,
                "save_dir": interaction.id,
            },
        )

    YEAR1: int = datetime.now(UTC).year + 1
    YEAR2: int = datetime.now(UTC).year + 2

    @helper.decorators.app_command(f"year_{YEAR1}", group=year_group)
    @helper.interactions.access_permitted_check()
    async def year_1(
        self,
        interaction: discord.Interaction,
        player: str | None = None,
        session: int | None = None,
    ) -> None:
        await interaction.response.defer()
        name, uuid = await helper.interactions.fetch_player_info(player, interaction)
        await self.year_command(interaction, name, uuid, session, self.YEAR1)

    @helper.decorators.app_command(f"year_{YEAR2}", group=year_group)
    @helper.interactions.access_permitted_check()
    async def year_2(
        self,
        interaction: discord.Interaction,
        player: str | None = None,
        session: int | None = None,
    ) -> None:
        await interaction.response.defer()
        name, uuid = await helper.interactions.fetch_player_info(player, interaction)

        discord_id = lib.accounts.uuid_to_discord_id(uuid)

        # Either command user or checked player has access
        condition_1 = False
        if discord_id is not None:
            condition_1 = Account(discord_id).permissions.has_access(f"year_{self.YEAR2}")

        condition_2 = Account(interaction.user.id).permissions.has_access(
            f"year_{self.YEAR2}"
        )

        if not condition_1 and not condition_2:
            embed = helper.Embeds.problems.no_premium__year_projection()
            await interaction.followup.send(embed=embed)
            return

        await self.year_command(interaction, name, uuid, session, self.YEAR2)


async def setup(client: helper.Client) -> None:
    await client.add_cog(YearCommandCog())
