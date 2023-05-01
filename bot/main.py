import os
import traceback

import discord
from discord.ext import commands
from discord import app_commands


# Initialise Bot
TOKEN = os.environ.get('STATALYTICS_TOKEN')

class MyClient(commands.Bot):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents, command_prefix=commands.when_mentioned_or('$'))

    async def setup_hook(self):
        cogs_list = ['sessions', 'linking', 'projection', 'shop', 'mostplayed', 'total',
                     'average', 'misc', 'resources', 'skin', 'practice', 'milestones',
                     'cosmetics', 'hotbar', 'compare']
        for ext in cogs_list:
            await client.load_extension(f'cogs.commands.{ext}')
        await self.tree.sync()

intents = discord.Intents.all()
client = MyClient(intents=intents)


@client.event
async def on_ready():
    print(f'Logged in as {client.user} (ID: {client.user.id})\n------')
    await client.change_presence(activity=discord.Game(name="/help"))


@client.tree.error
async def on_tree_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.CommandOnCooldown):
        await interaction.response.send_message(embed=discord.Embed(title="Command on cooldown!", description=f'Wait another `{round(error.retry_after, 2)}` and try again!\nPremium users bypass this restriction.', color=0xFFE100).set_thumbnail(url='https://media.discordapp.net/attachments/1027817138095915068/1076015715301208134/hourglass.png'), ephemeral=True)
    else:
        # show full error traceback
        traceback_str = ''.join(traceback.format_exception(type(error), error, error.__traceback__))
        print(traceback_str)
        channel = client.get_channel(1101006847831445585)
        await channel.send(f'```diff\n{traceback_str[-1988:]}\n```')

@client.command()
@commands.is_owner()
async def cog(ctx, method: str, cog_name: str):
    try:
        if method == 'enable':
            await client.load_extension(f'cogs.commands.{cog_name}')
            await client.tree.sync()
            msg = f'Successfully enabled cog: `{cog_name}`'
        elif method == 'disable':
            await client.unload_extension(f'cogs.commands.{cog_name}')
            await client.tree.sync()
            msg = f'Successfully disabled cog: `{cog_name}`'
        else:
            msg = 'Invalid method! Methods: `(enable, disable)`'
    except commands.errors.ExtensionNotFound:
        msg = f"Couldn't find cog: `{cog_name}`"
    await ctx.send(msg)


if __name__ == '__main__':
    client.run(TOKEN)
