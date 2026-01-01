from discord.ext import commands

import statalib as lib
import helper


class Management(commands.Cog):
    def __init__(self, client: helper.Client):
        self.client: helper.Client = client
        _ = self.client.remove_command("help")

    @commands.command()
    @commands.is_owner()
    async def sync(self, ctx: commands.Context[helper.Client]):
        _app_commands = await self.client.tree.sync()
        _ = await ctx.send('Successfully synced slash command tree!')

    @commands.command()
    async def help(self, ctx: commands.Context[helper.Client]):
        embed = helper.Embeds.help.help()

        _ = await ctx.send(embed=embed, view=helper.views.info.HelpMenuButtons())


async def setup(client: helper.Client) -> None:
    await client.add_cog(Management(client))
