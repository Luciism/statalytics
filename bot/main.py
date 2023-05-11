import os
import time
import traceback
from json import load as load_json
from json import dump as dump_json

import discord
from discord.ext import commands
from discord import app_commands


# Initialise Bot
TOKEN = os.environ.get('STATALYTICS_TOKEN')

class MyClient(commands.Bot):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents, command_prefix=commands.when_mentioned_or('$'))

    async def setup_hook(self):
        with open('./config.json', 'r') as datafile:
            cogs = load_json(datafile)['enabled_cogs']
        for ext in cogs:
            await client.load_extension(f'cogs.{ext}')
        await self.tree.sync()
        with open('./database/uptime.json', 'w') as datafile:
            dump_json({"start_time": time.time()}, datafile, indent=4)

intents = discord.Intents.all()
client = MyClient(intents=intents)


@client.event
async def on_ready():
    print(f'Logged in as {client.user} (ID: {client.user.id})\n------')
    await client.change_presence(activity=discord.Game(name="/help"))

@client.tree.error
async def on_tree_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.CommandOnCooldown):
        with open('./config.json', 'r') as datafile:
            config = load_json(datafile)
        embed_color = int(config['embed_warning_color'], base=16)
        embed = discord.Embed(title="Command on cooldown!", description=f'Wait another `{round(error.retry_after, 2)}` and try again!\nPremium users bypass this restriction.', color=embed_color)
        embed.set_thumbnail(url='https://media.discordapp.net/attachments/1027817138095915068/1076015715301208134/hourglass.png')
        await interaction.response.send_message(embed=embed, ephemeral=True)
    else:
        # show full error traceback
        traceback_str = ''.join(traceback.format_exception(type(error), error, error.__traceback__))
        print(traceback_str)

        channel = client.get_channel(1101006847831445585)
        if len(traceback_str) > 1988:
            for i in range(0, len(traceback_str), 1988):
                # Get the substring from i to i+max_length
                substring = traceback_str[i:i+1988]
                await channel.send(f'```cmd\n{substring}\n```')
        else:
            await channel.send(f'```cmd\n{traceback_str[-1988:]}\n```')

@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CommandNotFound):
        return
    raise error

@client.command()
@commands.is_owner()
async def load(ctx, cog: str):
    try:
        await client.load_extension(f'cogs.{cog}')
        msg = f'Successfully loaded cog: {cog}'
    except commands.errors.ExtensionNotFound:
        msg = f"Couldn't find cog: `{cog}`"
    await ctx.send(msg)

@client.command()
@commands.is_owner()
async def unload(ctx, cog: str):
    try:
        await client.unload_extension(f'cogs.{cog}')
        msg = f'Successfully unloaded cog: {cog}'
    except commands.errors.ExtensionNotFound:
        msg = f"Couldn't find cog: `{cog}`"
    await ctx.send(msg)

@client.command()
@commands.is_owner()
async def reload(ctx, cog: str):
    try:
        await client.reload_extension(f'cogs.{cog}')
        msg = f'Successfully reloaded cog: {cog}'
    except commands.errors.ExtensionNotFound:
        msg = f"Couldn't find cog: `{cog}`"
    except commands.errors.ExtensionNotLoaded:
        msg = f"Cog not loaded: `{cog}`"
    await ctx.send(msg)

@client.command()
@commands.is_owner()
async def sync(ctx):
    await client.tree.sync()
    await ctx.send('Successfully synced client tree!')

if __name__ == '__main__':
    client.run(TOKEN)
