from discord.ext import commands


class Management(commands.Cog):
    def __init__(self, client):
        self.client: commands.Bot = client


    @commands.command()
    @commands.is_owner()
    async def sync(self, ctx: commands.Context):
        await self.client.tree.sync()
        await ctx.send('Successfully synced slash command tree!')


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Management(client))
