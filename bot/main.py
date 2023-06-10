import os
import time
import traceback

from json import dump as dump_json

import discord
from discord.ext import commands
from discord import app_commands

from helper.functions import get_config, get_embed_color, log_error_msg


TOKEN = os.environ.get('STATALYTICS_TOKEN')


class MyClient(commands.Bot):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents, command_prefix=commands.when_mentioned_or('$'))

    async def setup_hook(self):
        cogs = get_config()['enabled_cogs']
        for ext in cogs:
            try:
                await client.load_extension(f'cogs.{ext}')
                print(f"Loaded cog: {ext}")
            except commands.errors.ExtensionNotFound:
                print(f"Cog doesn't exist: {ext}")
        await self.tree.sync()
        with open('./database/uptime.json', 'w') as datafile:
            dump_json({"start_time": time.time()}, datafile, indent=4)


intents = discord.Intents(messages=True)
intents.guilds = True
client = MyClient(intents=intents)


@client.event
async def on_ready():
    print(f'Logged in as {client.user} (ID: {client.user.id})\n------')
    await client.change_presence(activity=discord.Game(name="/help"))


@client.tree.error
async def on_tree_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    config = get_config()
    
    # Handle command cooldown errors
    if isinstance(error, app_commands.CommandOnCooldown):
        embed_color = get_embed_color(embed_type='warning')
        embed = discord.Embed(
            title="Command on cooldown!",
            description=f'Wait another `{round(error.retry_after, 2)}` and try again!\nPremium users bypass this restriction.',
            color=embed_color
        )
        embed.set_thumbnail(
            url='https://media.discordapp.net/attachments/1027817138095915068/1076015715301208134/hourglass.png')
        await interaction.response.send_message(embed=embed, ephemeral=True)

    # All other cases
    else:
        # respond to interaction with error embed
        try:
            embed_color = get_embed_color(embed_type='danger')
            embed = discord.Embed(
                title=f'An error occured running /{interaction.data["name"]}',
                description=f'```{error}```\nIf the problem persists, please [get in touch]({config["links"]["support_server"]})',
                color=embed_color
            )
            await interaction.edit_original_response(embed=embed)
        except discord.errors.NotFound:
            pass

        # log traceback to discord channel
        if os.environ.get('STATALYTICS_ENVIRONMENT') != 'development':
            await log_error_msg(client, error)


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
        msg = f'Successfully loaded cog: `{cog}`'
    except commands.errors.ExtensionNotFound:
        msg = f"Couldn't find cog: `{cog}`"
    except commands.errors.ExtensionAlreadyLoaded:
        msg = f"Cog already loaded: `{cog}`"
    await ctx.send(msg)


@client.command()
@commands.is_owner()
async def unload(ctx, cog: str):
    try:
        await client.unload_extension(f'cogs.{cog}')
        msg = f'Successfully unloaded cog: `{cog}`'
    except commands.errors.ExtensionNotFound:
        msg = f"Couldn't find cog: `{cog}`"
    except commands.errors.ExtensionNotLoaded:
        msg = f"Cog not loaded: `{cog}`"
    await ctx.send(msg)


@client.command()
@commands.is_owner()
async def reload(ctx, cog: str):
    try:
        await client.reload_extension(f'cogs.{cog}')
        msg = f'Successfully reloaded cog: `{cog}`'
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
