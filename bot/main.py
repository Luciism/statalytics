import os
import typing
import sqlite3
import traceback
import random
import json
from io import BytesIO

import discord
from mcuuid import MCUUID
from requests_cache import CachedSession
from discord import app_commands
from ui import ManageSession, SelectView, SubmitSuggestion

from link import link_account
from authenticate import authenticate_user
import initsession as initsession

from render.rendermostplayed import rendermostplayed
from render.rendertotal import rendertotal
from render.renderaverage import renderaverage
from render.renderresources import renderresources
from render.renderpractice import renderpractice
from render.rendermilestones import rendermilestones
from render.rendercosmetics import rendercosmetics
from render.rendershop import rendershop
from render.rendersession import rendersession
from render.renderprojection import renderprojection
from render.renderhotbar import renderhotbar

# Initialise Bot
TOKEN = os.environ.get('STATALYTICS_TOKEN', None)
MY_GUILD = discord.Object(id=981835717070159883)
NAME = "Statalytics"
GENERATING_MESSAGE = 'Generating please wait <a:loading1:1062561739989860462>'

stats_session = CachedSession(cache_name='cache/stats_cache', expire_after=300, ignored_parameters=['key'])
skin_session = CachedSession(cache_name='cache/skin_cache', expire_after=300, ignored_parameters=['key'])

class MyClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
    async def setup_hook(self):
        await self.tree.sync()


intents = discord.Intents.default()
intents.members = True
client = MyClient(intents=intents)


@client.event
async def on_ready():
    print(f'Logged in as {client.user} (ID: {client.user.id})')
    print('------')
    await client.change_presence(activity=discord.Game(name="/help"))

# Autofill
# Username
async def username_autocompletion(interaction: discord.Interaction, current: str) -> typing.List[app_commands.Choice[str]]: #pylint: disable=unused-argument
    data = []

    with sqlite3.connect('./database/autofill.db') as conn:
        cursor = conn.cursor()
        result = cursor.execute("SELECT * FROM autofill WHERE LOWER(username) LIKE LOWER(?)", (fr'%{current.lower()}%',))

    for row in result:
        if len(data) < 25:
            data.append(app_commands.Choice(name=row[2], value=row[2]))
        else:
            break
    return data

# Active sessions
async def session_autocompletion(interaction: discord.Interaction, current: str) -> typing.List[app_commands.Choice[str]]: #pylint: disable=unused-argument
    username_option = next((opt for opt in interaction.data['options'] if opt['name'] == 'username'), None)
    if username_option:
        username = username_option.get('value')
        uuid = MCUUID(name=username).uuid
    else:
        with sqlite3.connect('./database/linked_accounts.db') as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM linked_accounts WHERE discord_id = {interaction.user.id}")
            linked_data = cursor.fetchone()
        if not linked_data:
            return []
        uuid = linked_data[1]
    with sqlite3.connect('./database/sessions.db') as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM sessions WHERE uuid='{uuid}'")
        session_data = cursor.fetchall()
    data = []
    for session in session_data:
        data.append(app_commands.Choice(name=session[0], value=session[0]))
    return data

def check_subscription(interaction: discord.Interaction) -> typing.Optional[app_commands.Cooldown]:
    with sqlite3.connect('./database/subscriptions.db') as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM subscriptions WHERE discord_id = {interaction.user.id}")
        subscription = cursor.fetchone()
    if subscription:
        return app_commands.Cooldown(1, 0.0)
    return app_commands.Cooldown(1, 3.5)

# Get hypixel data
def get_hypixel_data(uuid: str):
    with open('./database/apikeys.json', 'r') as keyfile:
        allkeys = json.load(keyfile)['keys']
    key = random.choice(list(allkeys))

    return stats_session.get(f"https://api.hypixel.net/player?key={allkeys[key]}&uuid={uuid}", timeout=10).json()

def get_linked_data(discord_id: int):
    with sqlite3.connect('./database/linked_accounts.db') as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM linked_accounts WHERE discord_id = {discord_id}")
        return cursor.fetchone()

def get_subscription(discord_id: int):
    with sqlite3.connect('./database/subscriptions.db') as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM subscriptions WHERE discord_id = {discord_id}")
        return cursor.fetchone()

def update_command_stats(discord_id, command):
    with sqlite3.connect('./database/command_usage.db') as conn:
        cursor = conn.cursor()
        
        cursor.execute(f"SELECT * FROM overall WHERE discord_id = {discord_id}")
        if not cursor.fetchone(): cursor.execute('INSERT INTO overall (discord_id, commands_ran) VALUES (?, ?)', (discord_id, 1))
        else: cursor.execute(f'UPDATE overall SET commands_ran = commands_ran + 1 WHERE discord_id = {discord_id}')
        
        cursor.execute(f"SELECT * FROM {command} WHERE discord_id = {discord_id}")
        if not cursor.fetchone(): cursor.execute(f'INSERT INTO {command} (discord_id, commands_ran) VALUES (?, ?)', (discord_id, 1))
        else: cursor.execute(f'UPDATE {command} SET commands_ran = commands_ran + 1 WHERE discord_id = {discord_id}')
        
        cursor.execute(f'UPDATE overall SET commands_ran = commands_ran + 1 WHERE discord_id = 0')
        cursor.execute(f'UPDATE {command} SET commands_ran = commands_ran + 1 WHERE discord_id = 0')

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

# View Session Command
@client.tree.command(name = "session", description = "View the session stats of a player")
@app_commands.autocomplete(username=username_autocompletion, session=session_autocompletion)
@app_commands.describe(username='The player you want to view', session='The session you want to view')
@app_commands.checks.dynamic_cooldown(check_subscription)
async def session(interaction: discord.Interaction, username: str=None, session: int=None):
    # Get data for player
    try: name, uuid = await authenticate_user(username, interaction)
    except TypeError: return

    if session is None: session = 100

    # Bot responses Logic
    refined = name.replace('_', r'\_')
    with sqlite3.connect('./database/sessions.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM sessions WHERE session=? AND uuid=?", (int(str(session)[0]), uuid))
        session_data = cursor.fetchone()
        if not session_data:
            cursor.execute(f"SELECT * FROM sessions WHERE uuid='{uuid}' ORDER BY session ASC")
            session_data = cursor.fetchone()

    if not session_data:
        await interaction.response.defer()
        response = initsession.startsession(uuid, session=1)

        if response is True: await interaction.followup.send(f"**{refined}** has no active sessions so one was created!")
        else: await interaction.followup.send(f"**{refined}** has never played before!")
        return
    elif session_data[0] != session and session != 100: 
        await interaction.response.send_message(f"**{refined}** doesn't have an active session with ID: `{session}`!")
        return

    if session == 100: session = session_data[0]
    await interaction.response.send_message(GENERATING_MESSAGE)
    os.makedirs(f'./database/activerenders/{interaction.id}')
    hypixel_data = get_hypixel_data(uuid)

    rendersession(name, uuid, session, mode="Overall", hypixel_data=hypixel_data, save_dir=interaction.id)
    view = SelectView(name, user=interaction.user.id, inter=interaction, mode='Select a mode')
    await interaction.edit_original_response(content=None, attachments=[discord.File(f"./database/activerenders/{interaction.id}/overall.png")], view=view)
    rendersession(name, uuid, session, mode="Solos", hypixel_data=hypixel_data, save_dir=interaction.id)
    rendersession(name, uuid, session, mode="Doubles", hypixel_data=hypixel_data, save_dir=interaction.id)
    rendersession(name, uuid, session, mode="Threes", hypixel_data=hypixel_data, save_dir=interaction.id)
    rendersession(name, uuid, session, mode="Fours", hypixel_data=hypixel_data, save_dir=interaction.id)

    update_command_stats(interaction.user.id, 'session')

# Link Command
@client.tree.command(name = "link", description = "Link your account")
@app_commands.describe(username='The player you want to link to')
async def link(interaction: discord.Interaction, username: str):
    # Get name and uuid
    try:
        uuid = MCUUID(name=username).uuid
        name = MCUUID(name=username).name
    except Exception:
        await interaction.response.send_message("That player does not exist!")
        return

    # Linking Logic
    response = link_account(str(interaction.user), interaction.user.id, name, uuid)
    refined = name.replace('_', r'\_')
    if response is True: await interaction.response.send_message(f"Successfully linked to **{refined}** ({interaction.user})")
    # If discord isnt connected to hypixel
    else:
        await interaction.response.defer()
        if response is None:
            embed = discord.Embed(title=f"{refined}'s discord isn't connected on hypixel!", description='Example of how to connect your discord to hypixel:', color=0xFF00FF)
        else:
            embed = discord.Embed(title="How to connect discord to hypixel", description=f'''That player is connected to a different discord tag on hypixel!
                        If you own the **{refined}** account, you must __update your hypixel connection__ to match your current discord tag:''', color=0xFF00FF)
        embed.set_image(url='https://cdn.discordapp.com/attachments/1027817138095915068/1061647399266811985/result.gif')
        await interaction.followup.send(embed=embed)

# Unlink Command
@client.tree.command(name = "unlink", description = "Unlink your account")
async def unlink(interaction: discord.Interaction):
    with sqlite3.connect('./database/linked_accounts.db') as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM linked_accounts WHERE discord_id = {interaction.user.id}")
        if cursor.fetchone():
            cursor.execute(f"DELETE FROM linked_accounts WHERE discord_id = {interaction.user.id}")
            message = 'Successfully unlinked your account!'
        else: message = "You don't have an account linked! In order to link use `/link`!"
        await interaction.response.send_message(message)


# Create Session Command
@client.tree.command(name = "startsession", description = "Starts a new session")
async def start_session(interaction: discord.Interaction):
    linked_data = get_linked_data(interaction.user.id)

    if linked_data:
        await interaction.response.defer()
        uuid = linked_data[1]

        with sqlite3.connect('./database/sessions.db') as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM sessions WHERE uuid='{uuid}' ORDER BY session ASC")
            sessions = cursor.fetchall()

        subscription = get_subscription(interaction.user.id)

        if len(sessions) < 2 or subscription and len(sessions) < 5:
            for i, session in enumerate(sessions):
                if session[0] != i + 1:
                    sessionid = i + 1
                    initsession.startsession(uuid, session=sessionid)
                    break
            else:
                sessionid = len(sessions) + 1
                initsession.startsession(uuid, session=sessionid)
            await interaction.followup.send(f'A new session was successfully created! Session ID: `{sessionid}`')
        else:
            await interaction.followup.send('You already have the maximum sessions active for your plan! To remove a session use `/endsession <id>`!')
    else:
        await interaction.response.send_message("""You don't have an account linked! In order to link use `/link`!
                                                Otherwise use `/session <player>` will start a session if one doesn't already exist!""")


# Delete Session Command
@client.tree.command(name = "endsession", description = "Ends an active session")
@app_commands.autocomplete(session=session_autocompletion)
@app_commands.describe(session='The session you want to delete')
async def end_session(interaction: discord.Interaction, session: int = None):
    if session is None: session = 1

    linked_data = get_linked_data(interaction.user.id)

    if linked_data:
        uuid = linked_data[1]

        with sqlite3.connect('./database/sessions.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM sessions WHERE session=? AND uuid=?", (session, uuid))
            session_data = cursor.fetchone()
        if session_data:
            view = ManageSession(session, uuid, method="delete")
            await interaction.response.send_message(f'Are you sure you want to delete session {session}?', view=view, ephemeral=True)
            view.message = await interaction.original_response()
        else:
            await interaction.response.send_message(f"You don't have an active session with ID: `{session}`!")
    else:
        await interaction.response.send_message("You don't have an account linked! In order to link use `/link`!")


# Reset Session Command
@client.tree.command(name = "resetsession", description = "Resets an active session")
@app_commands.autocomplete(session=session_autocompletion)
@app_commands.describe(session='The session you want to reset')
async def reset_session(interaction: discord.Interaction, session: int = None):
    linked_data = get_linked_data(interaction.user.id)

    if linked_data:
        uuid = linked_data[1]

        if session is None: session = 1

        with sqlite3.connect('./database/sessions.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM sessions WHERE session=? AND uuid=?", (session, uuid))
            session_data = cursor.fetchone()

        if session_data:
            view = ManageSession(session, uuid, method="reset")
            await interaction.response.send_message(f'Are you sure you want to reset session {session}?', view=view, ephemeral=True)
            view.message = await interaction.original_response()
        else:
            await interaction.response.send_message(f"You don't have an active session with ID: `{session}`!")
    else:
        await interaction.response.send_message("You don't have an account linked! In order to link use `/link`!")


# Session List Command
@client.tree.command(name = "activesessions", description = "View all active sessions")
async def active_sessions(interaction: discord.Interaction):
    linked_data = get_linked_data(interaction.user.id)

    if linked_data:
        await interaction.response.defer()
        uuid = linked_data[1]

        with sqlite3.connect('./database/sessions.db') as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM sessions WHERE uuid='{uuid}'")
            sessions = cursor.fetchall()
        session_list = [str(session[0]) for session in sessions]

        if session_list:
            session_string = ", ".join(session_list)
            await interaction.followup.send(f'Your active sessions: `{session_string}`')
        else:
            await interaction.followup.send("You don't have any sessions active! Use `/startsession` to create one!")
    else:
        await interaction.response.send_message("You don't have an account linked! In order to link use `/link`!")


# Help command
@client.tree.command(name = "help", description = "Help Page")
async def get_help(interaction: discord.Interaction):
    with open('./assets/help.json', 'r') as datafile:
        embed_data = json.load(datafile)

    embeds = [discord.Embed.from_dict(embed) for embed in embed_data['embeds']]
    await interaction.response.send_message(embeds=embeds, ephemeral=True)

    update_command_stats(interaction.user.id, 'help')


# Invite
@client.tree.command(name='invite', description=f'Invite {NAME} to your server')
async def invite(interaction: discord.Interaction):
    await interaction.response.send_message(f'To add {NAME} to your server, [click here](https://discord.com/api/oauth2/authorize?client_id=903765373181112360&permissions=414464724033&scope=bot)')


# Projected stats
@client.tree.command(name = "prestige", description = "View the projected stats of a player")
@app_commands.autocomplete(username=username_autocompletion, session=session_autocompletion)
@app_commands.describe(username='The player you want to view', prestige='The prestige you want to view', session='The session you want to use as a benchmark (defaults to 1)')
@app_commands.checks.dynamic_cooldown(check_subscription)
async def projected_stats(interaction: discord.Interaction, prestige: int, username: str=None, session: int=None):
    try: name, uuid = await authenticate_user(username, interaction)
    except TypeError: return

    if session is None: session = 100

    # Bot responses Logic
    refined = name.replace('_', r'\_')
    with sqlite3.connect('./database/sessions.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM sessions WHERE session=? AND uuid=?", (int(str(session)[0]), uuid))
        session_data = cursor.fetchone()
        if not session_data:
            cursor.execute(f"SELECT * FROM sessions WHERE uuid='{uuid}' ORDER BY session ASC")
            session_data = cursor.fetchone()

    if not session_data:
        await interaction.response.defer()
        response = initsession.startsession(uuid, session=1)

        if response is True: await interaction.followup.send(f"**{refined}** has no active sessions so one was created!")
        else: await interaction.followup.send(f"**{refined}** has never played before!")
        return
    elif session_data[0] != session and session != 100: 
        await interaction.response.send_message(f"**{refined}** doesn't have an active session with ID: `{session}`!")
        return

    if session == 100: session = session_data[0]

    await interaction.response.send_message(GENERATING_MESSAGE)
    os.makedirs(f'./database/activerenders/{interaction.id}')
    skin_res = skin_session.get(f'https://visage.surgeplay.com/bust/144/{uuid}', timeout=10)

    hypixel_data = get_hypixel_data(uuid)
    
    try:
        current_star = renderprojection(name, uuid, session, mode="Overall", target=prestige, hypixel_data=hypixel_data, skin_res=skin_res.content, save_dir=interaction.id)
    except ZeroDivisionError:
        content = f"You can use `/bedwars` if you want current stats...\nUnless maybe an error occured? In which case please report this to the developers!"
        await interaction.edit_original_response(content=content)
        return
    
    view = SelectView(name, user=interaction.user.id, inter=interaction, mode='Select a mode')

    content = ":warning: THE LEVEL YOU ENTERED IS LOWER THAN THE CURRENT STAR! :warning:" if current_star > prestige else None
    await interaction.edit_original_response(content=content, attachments=[discord.File(f"./database/activerenders/{interaction.id}/overall.png")], view=view)
    renderprojection(name, uuid, session, mode="Solos", target=prestige, hypixel_data=hypixel_data, skin_res=skin_res.content, save_dir=interaction.id)
    renderprojection(name, uuid, session, mode="Doubles", target=prestige, hypixel_data=hypixel_data, skin_res=skin_res.content, save_dir=interaction.id)
    renderprojection(name, uuid, session, mode="Threes", target=prestige, hypixel_data=hypixel_data, skin_res=skin_res.content, save_dir=interaction.id)
    renderprojection(name, uuid, session, mode="Fours", target=prestige, hypixel_data=hypixel_data, skin_res=skin_res.content, save_dir=interaction.id)

    update_command_stats(interaction.user.id, 'projection')

# Shopkeeper
@client.tree.command(name = "shop", description = "View the shopkeeper of a player")
@app_commands.autocomplete(username=username_autocompletion)
@app_commands.describe(username='The player you want to view')
@app_commands.checks.dynamic_cooldown(check_subscription)
async def shop(interaction: discord.Interaction,username: str=None):
    try: name, uuid = await authenticate_user(username, interaction)
    except TypeError: return

    refined = name.replace('_', r'\_')
    await interaction.response.send_message(GENERATING_MESSAGE)

    hypixel_data = get_hypixel_data(uuid)
    rendered = rendershop(uuid, hypixel_data)
    if rendered is not False:
        await interaction.edit_original_response(content=None, attachments=[discord.File(rendered, filename="shop.png")])
    else: await interaction.edit_original_response(content=f'**{refined}** has not played before!')

    update_command_stats(interaction.user.id, 'shop')

# Most Played
@client.tree.command(name = "mostplayed", description = "Most played mode of a player")
@app_commands.autocomplete(username=username_autocompletion)
@app_commands.describe(username='The player you want to view')
@app_commands.checks.dynamic_cooldown(check_subscription)
async def most_played(interaction: discord.Interaction,username: str=None):
    try: name, uuid = await authenticate_user(username, interaction)
    except TypeError: return

    await interaction.response.send_message(GENERATING_MESSAGE)

    hypixel_data = get_hypixel_data(uuid)
    rendered = rendermostplayed(name, uuid, hypixel_data)
    await interaction.edit_original_response(content=None, attachments=[discord.File(rendered, filename='mostplayed.png')])

    update_command_stats(interaction.user.id, 'mostplayed')

# Suggest
@client.tree.command(name='suggest', description='Suggest a feature you would like to see added!')
async def suggest(interaction: discord.Interaction):
    channel = client.get_channel(1065918528236040232)
    await interaction.response.send_modal(SubmitSuggestion(channel))

# Total stats
@client.tree.command(name = "bedwars", description = "View the general stats of a player")
@app_commands.autocomplete(username=username_autocompletion)
@app_commands.describe(username='The player you want to view')
@app_commands.checks.dynamic_cooldown(check_subscription)
async def total(interaction: discord.Interaction, username: str=None):
    try: name, uuid = await authenticate_user(username, interaction)
    except TypeError: return

    await interaction.response.send_message(GENERATING_MESSAGE)
    os.makedirs(f'./database/activerenders/{interaction.id}')
    skin_res = skin_session.get(f'https://visage.surgeplay.com/bust/144/{uuid}', timeout=10)
    hypixel_data = get_hypixel_data(uuid)

    rendertotal(name, uuid, mode="Overall", hypixel_data=hypixel_data, skin_res=skin_res.content, save_dir=interaction.id, method="generic")
    view = SelectView(name, user=interaction.user.id, inter=interaction, mode='Select a mode')
    await interaction.edit_original_response(content=None, attachments=[discord.File(f"./database/activerenders/{interaction.id}/overall.png")], view=view)
    rendertotal(name, uuid, mode="Solos", hypixel_data=hypixel_data, skin_res=skin_res.content, save_dir=interaction.id, method="generic")
    rendertotal(name, uuid, mode="Doubles", hypixel_data=hypixel_data, skin_res=skin_res.content, save_dir=interaction.id, method="generic")
    rendertotal(name, uuid, mode="Threes", hypixel_data=hypixel_data, skin_res=skin_res.content, save_dir=interaction.id, method="generic")
    rendertotal(name, uuid, mode="Fours", hypixel_data=hypixel_data, skin_res=skin_res.content, save_dir=interaction.id, method="generic")

    update_command_stats(interaction.user.id, 'total')


# Average Stats
@client.tree.command(name = "average", description = "View the average stats of a player")
@app_commands.autocomplete(username=username_autocompletion)
@app_commands.describe(username='The player you want to view')
@app_commands.checks.dynamic_cooldown(check_subscription)
async def average(interaction: discord.Interaction, username: str=None):
    try: name, uuid = await authenticate_user(username, interaction)
    except TypeError: return

    await interaction.response.send_message(GENERATING_MESSAGE)
    os.makedirs(f'./database/activerenders/{interaction.id}')
    hypixel_data = get_hypixel_data(uuid)

    renderaverage(name, uuid, mode="Overall", hypixel_data=hypixel_data, save_dir=interaction.id)
    view = SelectView(name, user=interaction.user.id, inter=interaction, mode='Select a mode')
    await interaction.edit_original_response(content=None, attachments=[discord.File(f"./database/activerenders/{interaction.id}/overall.png")], view=view)
    renderaverage(name, uuid, mode="Solos", hypixel_data=hypixel_data, save_dir=interaction.id)
    renderaverage(name, uuid, mode="Doubles", hypixel_data=hypixel_data, save_dir=interaction.id)
    renderaverage(name, uuid, mode="Threes", hypixel_data=hypixel_data, save_dir=interaction.id)
    renderaverage(name, uuid, mode="Fours", hypixel_data=hypixel_data, save_dir=interaction.id)

    update_command_stats(interaction.user.id, 'average')

# Resources Stats
@client.tree.command(name = "resources", description = "View the resource stats of a player")
@app_commands.autocomplete(username=username_autocompletion)
@app_commands.describe(username='The player you want to view')
@app_commands.checks.dynamic_cooldown(check_subscription)
async def resources(interaction: discord.Interaction, username: str=None):
    try: name, uuid = await authenticate_user(username, interaction)
    except TypeError: return

    await interaction.response.send_message(GENERATING_MESSAGE)
    os.makedirs(f'./database/activerenders/{interaction.id}')
    hypixel_data = get_hypixel_data(uuid)

    renderresources(name, uuid, mode="Overall", hypixel_data=hypixel_data, save_dir=interaction.id)
    view = SelectView(name, user=interaction.user.id, inter=interaction, mode='Select a mode')
    await interaction.edit_original_response(content=None, attachments=[discord.File(f"./database/activerenders/{interaction.id}/overall.png")], view=view)
    renderresources(name, uuid, mode="Solos", hypixel_data=hypixel_data, save_dir=interaction.id)
    renderresources(name, uuid, mode="Doubles", hypixel_data=hypixel_data, save_dir=interaction.id)
    renderresources(name, uuid, mode="Threes", hypixel_data=hypixel_data, save_dir=interaction.id)
    renderresources(name, uuid, mode="Fours", hypixel_data=hypixel_data, save_dir=interaction.id)

    update_command_stats(interaction.user.id, 'resources')


# Skin View
@client.tree.command(name = "skin", description = "View the skin of a player")
@app_commands.autocomplete(username=username_autocompletion)
@app_commands.describe(username='The player you want to view')
@app_commands.checks.dynamic_cooldown(check_subscription)
async def skin(interaction: discord.Interaction, username: str=None):
    try: name, uuid = await authenticate_user(username, interaction)
    except TypeError: return

    refined = name.replace('_', r'\_')
    image_bytes = skin_session.get(f'https://visage.surgeplay.com/full/{uuid}', timeout=10).content
    file = discord.File(BytesIO(image_bytes), filename='skin.png')

    skin_embed = discord.Embed(title=f"{refined}'s skin", url= f"https://namemc.com/profile/{uuid}", description=f"Click [here](https://crafatar.com/skins/{uuid}) to download", color=0x00AFF4)
    skin_embed.set_image(url="attachment://skin.png")
    await interaction.response.send_message(file=file, embed=skin_embed)

    update_command_stats(interaction.user.id, 'skin')


# Practice Stats
@client.tree.command(name = "practice", description = "View the practice stats of a player")
@app_commands.autocomplete(username=username_autocompletion)
@app_commands.describe(username='The player you want to view')
@app_commands.checks.dynamic_cooldown(check_subscription)
async def practice(interaction: discord.Interaction, username: str=None):
    try: name, uuid = await authenticate_user(username, interaction)
    except TypeError: return

    await interaction.response.send_message(GENERATING_MESSAGE)

    hypixel_data = get_hypixel_data(uuid)
    rendered = renderpractice(name, uuid, hypixel_data)
    await interaction.edit_original_response(content=None, attachments=[discord.File(rendered, filename='practice.png')])

    update_command_stats(interaction.user.id, 'practice')


# Milestone Stats
@client.tree.command(name = "milestones", description = "View the milestone stats of a player")
@app_commands.autocomplete(username=username_autocompletion, session=session_autocompletion)
@app_commands.describe(username='The player you want to view', session='The session you want to use (0 for none, defaults to 1 if active)')
@app_commands.checks.dynamic_cooldown(check_subscription)
async def milestones(interaction: discord.Interaction, username: str=None, session: int=None):
    try: name, uuid = await authenticate_user(username, interaction)
    except TypeError: return

    if session is None: session = 100
    with sqlite3.connect('./database/sessions.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM sessions WHERE session=? AND uuid=?", (int(str(session)[0]), uuid))
        if not cursor.fetchone() and not session in (0, 100):
            await interaction.response.send_message(f"`{username}` doesn't have an active session with ID: `{session}`!\nSelect a valid session or specify `0` in order to not use session data!")
            return

    await interaction.response.send_message(GENERATING_MESSAGE)
    os.makedirs(f'./database/activerenders/{interaction.id}')
    session = 1 if session == 100 else session
    hypixel_data = get_hypixel_data(uuid)

    rendermilestones(name, uuid, mode="Overall", session=session, hypixel_data=hypixel_data, save_dir=interaction.id)
    view = SelectView(name, user=interaction.user.id, inter=interaction, mode='Select a mode')
    await interaction.edit_original_response(content=None, attachments=[discord.File(f"./database/activerenders/{interaction.id}/overall.png")], view=view)
    rendermilestones(name, uuid, mode="Solos", session=session, hypixel_data=hypixel_data, save_dir=interaction.id)
    rendermilestones(name, uuid, mode="Doubles", session=session, hypixel_data=hypixel_data, save_dir=interaction.id)
    rendermilestones(name, uuid, mode="Threes", session=session, hypixel_data=hypixel_data, save_dir=interaction.id)
    rendermilestones(name, uuid, mode="Fours", session=session, hypixel_data=hypixel_data, save_dir=interaction.id)

    update_command_stats(interaction.user.id, 'milestones')


# Active Cosmetics
@client.tree.command(name = "activecosmetics", description = "View the practice stats of a player")
@app_commands.autocomplete(username=username_autocompletion)
@app_commands.describe(username='The player you want to view')
@app_commands.checks.dynamic_cooldown(check_subscription)
async def active_cosmetics(interaction: discord.Interaction, username: str=None):
    try: name, uuid = await authenticate_user(username, interaction)
    except TypeError: return

    await interaction.response.send_message(GENERATING_MESSAGE)

    hypixel_data = get_hypixel_data(uuid)
    rendered = rendercosmetics(name, uuid, hypixel_data)
    await interaction.edit_original_response(content=None, attachments=[discord.File(rendered, filename='cosmetics.png')])

    update_command_stats(interaction.user.id, 'cosmetics')


# Hotbar
@client.tree.command(name = "hotbar", description = "View the hotbar preferences of a player")
@app_commands.autocomplete(username=username_autocompletion)
@app_commands.describe(username='The player you want to view')
@app_commands.checks.dynamic_cooldown(check_subscription)
async def hotbar(interaction: discord.Interaction,username: str=None):
    try: name, uuid = await authenticate_user(username, interaction)
    except TypeError: return

    refined = name.replace('_', r'\_')
    await interaction.response.send_message(GENERATING_MESSAGE)

    hypixel_data = get_hypixel_data(uuid)
    rendered = renderhotbar(name, uuid, hypixel_data)
    if rendered is not False:
        await interaction.edit_original_response(content=None, attachments=[discord.File(rendered, filename="hotbar.png")])
    else: await interaction.edit_original_response(content=f'**{refined}** does not have a hotbar set!**')

    update_command_stats(interaction.user.id, 'hotbar')

# Pointless stats
@client.tree.command(name = "pointless", description = "View the general pointless stats of a player")
@app_commands.autocomplete(username=username_autocompletion)
@app_commands.describe(username='The player you want to view')
@app_commands.checks.dynamic_cooldown(check_subscription)
async def pointless(interaction: discord.Interaction, username: str=None):
    try: name, uuid = await authenticate_user(username, interaction)
    except TypeError: return

    await interaction.response.send_message(GENERATING_MESSAGE)
    os.makedirs(f'./database/activerenders/{interaction.id}')
    skin_res = skin_session.get(f'https://visage.surgeplay.com/bust/144/{uuid}', timeout=10)
    hypixel_data = get_hypixel_data(uuid)

    rendertotal(name, uuid, mode="Overall", hypixel_data=hypixel_data, skin_res=skin_res.content, save_dir=interaction.id, method="pointless")
    view = SelectView(name, user=interaction.user.id, inter=interaction, mode='Select a mode')
    await interaction.edit_original_response(content=None, attachments=[discord.File(f"./database/activerenders/{interaction.id}/overall.png")], view=view)
    rendertotal(name, uuid, mode="Solos", hypixel_data=hypixel_data, skin_res=skin_res.content, save_dir=interaction.id, method="pointless")
    rendertotal(name, uuid, mode="Doubles", hypixel_data=hypixel_data, skin_res=skin_res.content, save_dir=interaction.id, method="pointless")
    rendertotal(name, uuid, mode="Threes", hypixel_data=hypixel_data, skin_res=skin_res.content, save_dir=interaction.id, method="pointless")
    rendertotal(name, uuid, mode="Fours", hypixel_data=hypixel_data, skin_res=skin_res.content, save_dir=interaction.id, method="pointless")

    update_command_stats(interaction.user.id, 'pointless')

# Usage command
@client.tree.command(name = "usage", description = "View Command Usage")
async def usage_stats(interaction: discord.Interaction):
    with open('./assets/command_map.json', 'r') as datafile:
        command_map = json.load(datafile)['commands']

    with sqlite3.connect('./database/command_usage.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [table[0] for table in cursor.fetchall()]

        cursor.execute(f'SELECT * FROM overall WHERE discord_id = {interaction.user.id}')
        table_data = cursor.fetchone()
        if not table_data: table_data = (0, 0)
        description = [f'**Overall - {table_data[1]}**\n\n']

        for table in tables:
            cursor.execute(f'SELECT * FROM {table} WHERE discord_id = {interaction.user.id}')
            table_data = cursor.fetchone()
            if not table_data: table_data = (0, 0)
            if table != "overall":
                description.append(f'`{command_map.get(table)}` - `{table_data[1]}`\n')

    embed = discord.Embed(title="Your Command Usage", description=''.join(description), color=0x5865F2)
    await interaction.response.send_message(embed=embed)

client.run(TOKEN)
