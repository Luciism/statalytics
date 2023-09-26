from discord.ext import commands

class ManageCogs(commands.Cog):
    def __init__(self, client):
        self.client: commands.Bot = client


    async def _check_cog(self, cog: str):
        # `False` if cog == this file
        if cog == __name__.removeprefix('cogs.'):
            return False
        return True


    @commands.command()
    @commands.is_owner()
    async def load(self, ctx: commands.context.Context, cog: str):
        if not await self._check_cog(cog):
            await ctx.send('That cog cannot be managed!')
            return

        try:
            await self.client.load_extension(f'cogs.{cog}')
            msg = f'Successfully loaded cog: `{cog}`'
        except commands.errors.ExtensionNotFound:
            msg = f"Couldn't find cog: `{cog}`"
        except commands.errors.ExtensionAlreadyLoaded:
            msg = f"Cog already loaded: `{cog}`"
        await ctx.send(msg)


    @commands.command()
    @commands.is_owner()
    async def unload(self, ctx: commands.context.Context, cog: str):
        if not await self._check_cog(cog):
            await ctx.send('That cog cannot be managed!')
            return

        try:
            await self.client.unload_extension(f'cogs.{cog}')
            msg = f'Successfully unloaded cog: `{cog}`'
        except commands.errors.ExtensionNotFound:
            msg = f"Couldn't find cog: `{cog}`"
        except commands.errors.ExtensionNotLoaded:
            msg = f"Cog not loaded: `{cog}`"
        await ctx.send(msg)


    @commands.command()
    @commands.is_owner()
    async def reload(self, ctx: commands.context.Context, cog: str):
        if not await self._check_cog(cog):
            await ctx.send('That cog cannot be managed!')
            return

        try:
            await self.client.reload_extension(f'cogs.{cog}')
            msg = f'Successfully reloaded cog: `{cog}`'
        except commands.errors.ExtensionNotFound:
            msg = f"Couldn't find cog: `{cog}`"
        except commands.errors.ExtensionNotLoaded:
            msg = f"Cog not loaded: `{cog}`"
        await ctx.send(msg)


async def setup(client: commands.Bot) -> None:
    await client.add_cog(ManageCogs(client))
