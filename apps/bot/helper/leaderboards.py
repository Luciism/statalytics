import logging
import math
from typing import AsyncGenerator

import discord
import statalib as lib
from statalib.hypixel.lbs import LeaderboardData, LeaderboardPlayerEntry

from render.leaderboards import render_leaderboard_chunk


async def generate_leaderboard_images(
    lb: LeaderboardData,
) -> AsyncGenerator[tuple[discord.File, int, int], None]:
    players = lib.hypixel.lbs.fetch.fetch_leaderboard_players(lb)

    # files: list[discord.File] = []

    entries_per_img = 10
    total_entries = len(lb.leaders)
    total_groups = math.ceil(total_entries / entries_per_img)

    i = 0
    profiles: list[LeaderboardPlayerEntry] = []
    async for profile in players:
        logging.info(f"Received profile: {profile.username} - {profile.value}")
        profiles.append(profile)

        if (i + 1) % entries_per_img == 0 or i + 1 == total_entries:
            # Last partial set of entries
            if (i + 1) % entries_per_img != 0 and i + 1 == total_entries:
                starting_pos = (i + 1) - (i + 1) % entries_per_img + 1
                image_index = total_groups - 1
            else:
                starting_pos = (i + 1) - entries_per_img + 1
                image_index = int((i - (entries_per_img - 1)) / entries_per_img)

            lb_img = await render_leaderboard_chunk(
                lb,
                profiles,
                starting_pos=starting_pos,
                include_header=i + 1 == entries_per_img,
            )

            # files.append(discord.File(lb_img, filename=f"lb-{image_index}.png"))
            file = discord.File(lb_img, filename=f"lb-{image_index}.png")
            yield file, image_index + 1, total_groups

            profiles = []

        i += 1

    # return files


async def generate_embeds_for_leaderboard_path(
    lb_path: str,
) -> tuple[list[discord.Embed], list[discord.File]]:
    bedwars_lbs = await lib.hypixel.lbs.fetch_bedwars_leaderboards()
    try:
        lb = [lb for lb in bedwars_lbs if lb.info.path == lb_path][0]
    except IndexError as exc:
        raise ValueError(f"Leaderboard path '{lb_path}' is invalid!") from exc

    files: list[discord.File] = []

    async for image, _, _ in generate_leaderboard_images(lb):
        files.append(image)

    embeds = [
        discord.Embed(color=0x202026).set_image(url=f"attachment://{file.filename}")
        for file in files
    ]

    embeds[0].title = f"{lb.info.prefix} {lb.info.title} Leaderboard"

    return embeds, files
