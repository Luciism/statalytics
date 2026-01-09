import discord
from discord.ext import commands

import helper


class WhoCommandCog(commands.Cog):
    @helper.decorators.app_command("who")
    @helper.interactions.access_permitted_check()
    async def who(self, interaction: discord.Interaction, player: str | None=None):
        name, uuid = await helper.interactions.fetch_player_info(player, interaction, eph=True)

        dashed_uuid = "-".join([uuid[0:8], uuid[8:12], uuid[12:16], uuid[16:20], uuid[20:32]])

        if player is None or len(player) <= 16:
            await interaction.response.send_message(
                f'UUID for **{name}** -> `{uuid}` (`{dashed_uuid}`)', ephemeral=True)
        else:
            await interaction.response.send_message(
                f'Username for **{uuid}** -> `{name}`', ephemeral=True)


async def setup(client: helper.Client) -> None:
    await client.add_cog(WhoCommandCog())
