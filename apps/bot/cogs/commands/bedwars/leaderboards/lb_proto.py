import discord
import statalib as lib
from discord import app_commands
from discord.ext import commands

import helper

class BedwarsStarsLeaderboard(commands.Cog):
    def __init__(self, client: helper.Client):
        self.client: helper.Client = client
        self.LOADING_MSG = lib.config.loading_message()
        
    @app_commands.command(name="leaderboard_proto", description="Test")
    async def stars_lb(self, interaction: discord.Interaction):
        emoji = "<a:loading1:1062561739989860462>"
        await interaction.response.send_message(f"Generating {emoji}", ephemeral=True)

        bedwars_lbs = await lib.hypixel.lbs.fetch_bedwars_leaderboards()
        lb = [lb for lb in bedwars_lbs if lb.info.path == "wins_new"][0]

        files = []

        async for image, i, total in helper.leaderboards.generate_leaderboard_images(lb):
            files.append(image) 
            _ = await interaction.edit_original_response(
                content=f"Generating ({i} / {total}) {emoji}"
            )

            # embed = discord.Embed(color=0x202026).set_image(
            #     url=f"attachment://{files[-1].filename}"
            # )
            # _ = await interaction.channel.send(
            #     content="", embed=embed, file=files[-1]
            # )

        embeds = [
            discord.Embed(color=0x202026).set_image(url=f"attachment://{file.filename}")
            for file in files
        ]
        await interaction.channel.send(files=files, embeds=embeds)


async def setup(client: helper.Client) -> None:
    await client.add_cog(BedwarsStarsLeaderboard(client))
