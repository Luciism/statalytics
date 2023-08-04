import time
from os import getenv
from json import dump as dump_json

import discord
from discord.ext import commands
from discord import app_commands

from dotenv import load_dotenv
load_dotenv()

from statalib import (
    PlayerNotFoundError,
    SessionNotFoundError,
    HypixelInvalidResponseError,
    add_info_view,
    handle_cooldown_error,
    handle_hypixel_error,
    handle_all_errors,
    get_config,
)


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

        add_info_view(self)

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
async def on_tree_error(interaction: discord.Interaction,
                        error: app_commands.AppCommandError):
    if isinstance(error, PlayerNotFoundError):
        return

    if isinstance(error, SessionNotFoundError):
        return

    if isinstance(error, app_commands.CommandOnCooldown):
        await handle_cooldown_error(interaction, error)
        return

    if isinstance(error, HypixelInvalidResponseError):
        await handle_hypixel_error(interaction)
        return

    await handle_all_errors(interaction, client, error)


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
    client.run(getenv('BOT_TOKEN'))
