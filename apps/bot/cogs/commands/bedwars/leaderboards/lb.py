from copy import deepcopy
import math
from typing import final

import cachetools
import discord
import statalib as lib
from cachetools_async import cached
from discord import app_commands
from discord.ext import commands
from statalib.hypixel.lbs import LeaderboardData

import helper
from helper.views import PaginationView
from render.leaderboards import render_leaderboard_chunk
from helper import emoji

PAGE_SIZE = 10


@cached(cache=cachetools.TTLCache(maxsize=20, ttl=60 * 60 * 6))
async def render_leaderboard_page(lb: LeaderboardData, page: int):
    lb_page = LeaderboardData(
        info=lb.info,
        leaders=lb.leaders[(page - 1) * PAGE_SIZE : page * PAGE_SIZE],
        count=PAGE_SIZE,
    )

    players = [p async for p in lib.hypixel.lbs.fetch.fetch_leaderboard_players(lb_page)]

    lb_img = await render_leaderboard_chunk(
        lb_page,
        players,
        starting_pos=(page-1) * PAGE_SIZE + 1,
        include_header=True
    )

    file = discord.File(lb_img, filename=f"lb-page.png")
    return file
    

@final
class LeaderboardCommandsCog(commands.Cog):
    def __init__(self, client: helper.Client):
        self.client = client
        self.LOADING_MSG = lib.config.loading_message()

    lb_group = app_commands.Group(
        name="leaderboard",
        description="View a leaderboard.",
        allowed_contexts=app_commands.AppCommandContext(
            guild=True, dm_channel=True, private_channel=True
        ),
        allowed_installs=app_commands.AppInstallationType(guild=True, user=True),
    )

    async def compact_lb_command(self, interaction: discord.Interaction, lb_path: str) -> None:
        await interaction.response.send_message(f"Generating {emoji.LOADING}")

        bedwars_lbs = await lib.hypixel.lbs.fetch_bedwars_leaderboards()
        lb = [lb for lb in bedwars_lbs if lb.info.path == lb_path][0]

        async def change_page(page: int) -> None:
            image_file = await render_leaderboard_page(lb, page)

            _ = await interaction.edit_original_response(attachments=[deepcopy(image_file)])

        view = PaginationView(
            interaction=interaction,
            callback=change_page,
            page=1,
            total_pages=math.ceil(len(lb.leaders) / PAGE_SIZE),
        )

        image_file = await render_leaderboard_page(lb, 1)

        embed = discord.Embed(
            title=f"{lb.info.prefix} {lb.info.title} Leaderboard", color=0x202026
        ).set_image(url="attachment://lb-page.png")

        _ = await interaction.edit_original_response(
            content="", attachments=[deepcopy(image_file)], embed=embed, view=view
        )


    @lb_group.command(name="level", description="View the Bedwars level leaderboard.")
    @app_commands.checks.dynamic_cooldown(helper.generic_command_cooldown)
    async def stars_lb(self, interaction: discord.Interaction):
        await self.compact_lb_command(interaction, "bedwars_level")
        lib.usage.update_command_stats(interaction.user.id, "bedwars_level_lb")

    @lb_group.command(name="wins", description="View the Bedwars overall wins leaderboard.")
    @app_commands.checks.dynamic_cooldown(helper.generic_command_cooldown)
    async def wins_lb(self, interaction: discord.Interaction):
        await self.compact_lb_command(interaction, "wins_new")
        lib.usage.update_command_stats(interaction.user.id, "bedwars_wins_lb")

    @lb_group.command(name="finals", description="View the Bedwars overall final kills leaderboard.")
    @app_commands.checks.dynamic_cooldown(helper.generic_command_cooldown)
    async def final_kills_lb(self, interaction: discord.Interaction):
        await self.compact_lb_command(interaction, "final_kills_new")
        lib.usage.update_command_stats(interaction.user.id, "bedwars_final_kills_lb")

async def setup(client: helper.Client) -> None:
    await client.add_cog(LeaderboardCommandsCog(client))
