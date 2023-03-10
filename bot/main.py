import os
import typing
import sqlite3
import traceback
import random
import json
from io import BytesIO

import requests
import discord
from mcuuid import MCUUID
from discord import app_commands, ui
from ui import DeleteSession, SelectView

from link import AccountLink
from authenticate import authenticate_user
import reqapi

from render.rendergraph import rendergraph
from render.rendertotal import rendertotal
from render.renderratio import renderratio
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

    with sqlite3.connect(f'{os.getcwd()}/database/autofill.db') as conn:
        cursor = conn.cursor()
        result = cursor.execute("SELECT * FROM autofill WHERE LOWER(username) LIKE LOWER(?)", (fr'%{current.lower()}%',))

    for row in result:
        if len(data) < 25:
            data.append(app_commands.Choice(name=row[0], value=row[0]))
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
        with sqlite3.connect(f'{os.getcwd()}/database/linkedaccounts.db') as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM linkedaccounts WHERE discordid = '{interaction.user.id}'")
            linked_data = cursor.fetchone()
        if not linked_data:
            return []
        uuid = linked_data[3]
    with sqlite3.connect(f'{os.getcwd()}/database/sessions.db') as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM sessions WHERE uuid='{uuid}'")
        session_data = cursor.fetchall()
    data = []
    for session in session_data:
        data.append(app_commands.Choice(name=session[0], value=session[0]))
    return data

def check_subscription(interaction: discord.Interaction) -> typing.Optional[app_commands.Cooldown]:
    with sqlite3.connect(f'{os.getcwd()}/database/subscriptions.db') as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM subscriptions WHERE discordid = '{interaction.user.id}'")
        subscription = cursor.fetchone()
    if subscription:
        return app_commands.Cooldown(1, 0.0)
    return app_commands.Cooldown(1, 3.5)

# Get hypixel data
def get_hypixel_data(uuid):
    with open(f'{os.getcwd()}/database/apikeys.json', 'r') as keyfile:
        allkeys = json.load(keyfile)['keys']
    key = random.choice(list(allkeys))

    return requests.get(f"https://api.hypixel.net/player?key={allkeys[key]}&uuid={uuid}", timeout=10).json()

@client.tree.error
async def on_tree_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.CommandOnCooldown):
        await interaction.response.send_message(embed=discord.Embed(title="Command on cooldown!", description=f'Wait another `{round(error.retry_after, 2)}` and try again!\nPremium users bypass this restriction.', color=0xFFE100).set_thumbnail(url='https://media.discordapp.net/attachments/1027817138095915068/1076015715301208134/hourglass.png'), ephemeral=True)
    else:
        # show full error traceback
        traceback.print_exception(type(error), error, error.__traceback__)

# View Session Command
@client.tree.command(name = "session", description = "View the session stats of a player")
@app_commands.autocomplete(username=username_autocompletion, session=session_autocompletion)
@app_commands.describe(username='The player you want to view', session='The session you want to view')
@app_commands.checks.dynamic_cooldown(check_subscription)
async def session(interaction: discord.Interaction, username: str=None, session: int=None):
    # Get data for player
    try:
        name, uuid = await authenticate_user(username, interaction)
    except Exception:
        await interaction.response.send_message("That player doesn't exist!")
        return
    if session is None:
        session = 1

    # Bot responses Logic
    refined = name.replace('_', r'\_')
    with sqlite3.connect(f'{os.getcwd()}/database/sessions.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM sessions WHERE session=? AND uuid=?", (session, uuid))
        if cursor.fetchone():
            await interaction.response.send_message('Generating please wait <a:loading1:1062561739989860462>')
            interid = await interaction.original_response()
            os.makedirs(f'{os.getcwd()}/database/activerenders/{interid.id}')
            hypixel_data = get_hypixel_data(uuid)

            rendersession(name, uuid, session, mode="Overall", hypixel_data=hypixel_data, save_dir=interid.id)
            view = SelectView(name, user=interaction.user.id, interid=interid, inter=interaction, mode='Select a mode')
            await interaction.edit_original_response(content=None, attachments=[discord.File(f"{os.getcwd()}/database/activerenders/{interid.id}/overall.png")], view=view)
            rendersession(name, uuid, session, mode="Solos", hypixel_data=hypixel_data, save_dir=interid.id)
            rendersession(name, uuid, session, mode="Doubles", hypixel_data=hypixel_data, save_dir=interid.id)
            rendersession(name, uuid, session, mode="Threes", hypixel_data=hypixel_data, save_dir=interid.id)
            rendersession(name, uuid, session, mode="Fours", hypixel_data=hypixel_data, save_dir=interid.id)
        else:
            cursor.execute(f"SELECT * FROM sessions WHERE uuid='{uuid}'")
            if not cursor.fetchone():
                await interaction.response.defer()
                returnvalue = reqapi.startsession(uuid, session=1)
                if returnvalue is True:
                    await interaction.followup.send(f"**{refined}** has no active sessions so one was created!")
                else:
                    await interaction.followup.send(f"{refined} has never played before!")
            else:
                await interaction.response.send_message(f"{refined} doesn't have an active session with ID: `{session}`!")

# Link Command
@client.tree.command(name = "link", description = "Link your account")
@app_commands.describe(username='The player you want to link to')
async def link(interaction: discord.Interaction, username: str):
    # Get name and uuid
    try:
        uuid = MCUUID(name=username).uuid
        name = MCUUID(name=username).name
    except Exception:
        await interaction.response.send_message("That player doesn't exist!")
        await interaction.response.send_message("That player does not exist!")
        return

    # Linking Logic
    response = AccountLink(str(interaction.user), interaction.user.id, name, uuid).account_link()
    refined = name.replace('_', r'\_')
    if response is True:
        await interaction.response.send_message(f"Successfully linked to {refined} ({interaction.user})")
    # If discord isnt connected to hypixel
    elif response is None:
        await interaction.response.defer()
        embed_var = discord.Embed(title=f"{refined}'s discord isn't connected on hypixel!", description='Example of how to connect your discord to hypixel:', color=0xFF00FF)
        embed_var.set_image(url='https://cdn.discordapp.com/attachments/1027817138095915068/1061647399266811985/result.gif')
        await interaction.response.send_message(embed=embed_var)
    else:
        await interaction.response.defer()
        embed_var = discord.Embed(title="How to connect discord to hypixel", description=f'That player is connected to a different discord tag on hypixel!\nIf you own the {refined} account, you must __update your hypixel connection__ to match your current discord tag:', color=0xFF00FF)
        embed_var.set_image(url='https://cdn.discordapp.com/attachments/1027817138095915068/1061647399266811985/result.gif')
        await interaction.followup.send(embed=embed_var)

# Unlink Command
@client.tree.command(name = "unlink", description = "Unlink your account")
async def unlink(interaction: discord.Interaction):
    with sqlite3.connect(f'{os.getcwd()}/database/linkedaccounts.db') as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM linkedaccounts WHERE discordid = '{interaction.user.id}'")
        if cursor.fetchone():
            cursor.execute(f"DELETE FROM linkedaccounts WHERE discordid = '{interaction.user.id}'")
            conn.commit()
            await interaction.response.send_message('Successfully unlinked your account!')
        else:
            await interaction.response.send_message("You don't have an account linked! In order to link use `/link`!")


# Create Session Command
@client.tree.command(name = "startsession", description = "Starts a new session")
async def start_session(interaction: discord.Interaction):
    with sqlite3.connect(f'{os.getcwd()}/database/linkedaccounts.db') as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM linkedaccounts WHERE discordid = '{interaction.user.id}'")
        linked_data = cursor.fetchone()
    if linked_data:
        await interaction.response.defer()
        uuid = linked_data[3]
        with sqlite3.connect(f'{os.getcwd()}/database/sessions.db') as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM sessions WHERE uuid='{uuid}' ORDER BY session ASC")
            sessions = cursor.fetchall()
        with sqlite3.connect(f'{os.getcwd()}/database/subscriptions.db') as conn:
            cursor = conn.cursor()
            query = f"SELECT * FROM subscriptions WHERE discordid = '{interaction.user.id}'"
            cursor.execute(query)
            subsciption = cursor.fetchone()
        if len(sessions) < 2 or subsciption and len(sessions) < 5:
            for i, session in enumerate(sessions):
                if session[0] != i + 1:
                    sessionid = i + 1
                    reqapi.startsession(uuid, session=sessionid)
                    break
            else:
                sessionid = len(sessions) + 1
                reqapi.startsession(uuid, session=sessionid)
            await interaction.followup.send(f'A new session was successfully created! Session ID: {sessionid}')
        else:
            await interaction.followup.send('You already have the maximum sessions active for your plan! To remove a session use `/endsession <id>`!')
    else:
        await interaction.response.send_message("You don't have an account linked! In order to link use `/link`!\nOtherwise use `/session <player>` will start a session if one doesn't already exist!")


# Delete Session Command
@client.tree.command(name = "endsession", description = "Ends an active session")
@app_commands.autocomplete(session=session_autocompletion)
@app_commands.describe(session='The session you want to delete')
async def end_session(interaction: discord.Interaction, session: int = None):
    if session is None:
        session = 1
    with sqlite3.connect(f'{os.getcwd()}/database/linkedaccounts.db') as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM linkedaccounts WHERE discordid = '{interaction.user.id}'")
        linked_data = cursor.fetchone()
    if linked_data:
        uuid = linked_data[3]

        with sqlite3.connect(f'{os.getcwd()}/database/sessions.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM sessions WHERE session=? AND uuid=?", (session, uuid))
            session_data = cursor.fetchone()
        if session_data:
            view = DeleteSession(session, uuid, method="delete")
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
    with sqlite3.connect(f'{os.getcwd()}/database/linkedaccounts.db') as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM linkedaccounts WHERE discordid = '{interaction.user.id}'")
        linked_data = cursor.fetchone()

    if linked_data:
        uuid = linked_data[3]

        if session is None:
            session = 1

        with sqlite3.connect(f'{os.getcwd()}/database/sessions.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM sessions WHERE session=? AND uuid=?", (session, uuid))
            session_data = cursor.fetchone()
        if session_data:
            view = DeleteSession(session, uuid, method="reset")
            await interaction.response.send_message(f'Are you sure you want to reset session {session}?', view=view, ephemeral=True)
            view.message = await interaction.original_response()
        else:
            await interaction.response.send_message(f"You don't have an active session with ID: `{session}`!")
    else:
        await interaction.response.send_message("You don't have an account linked! In order to link use `/link`!")


# Session List Command
@client.tree.command(name = "activesessions", description = "View all active sessions")
async def active_sessions(interaction: discord.Interaction):
    with sqlite3.connect(f'{os.getcwd()}/database/linkedaccounts.db') as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM linkedaccounts WHERE discordid = '{interaction.user.id}'")
        linked_data = cursor.fetchone()
    if linked_data:
        await interaction.response.defer()
        uuid = linked_data[3]

        with sqlite3.connect(f'{os.getcwd()}/database/sessions.db') as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM sessions WHERE uuid='{uuid}'")
            sessions = cursor.fetchall()
        session_list = []
        for session in sessions:
            session_list.append(str(session[0]))

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
    embed_var = discord.Embed(title=f"{NAME} Help Menu", description=None, color=0x46C5F0)
    embed_var.add_field(name='How To Use', value=f'To use {NAME}, start by linking your account with `/link` - this step is not required but is recommending for the best functionality as you will not have to constantly input your username. Please note that the `/prestige` commands requires an active session to benchmark your current skill level!', inline=False)
    embed_var.add_field(name='List Of Commands', value="`/session` - view an active session of a player\n`/startsession` - starts a new session\n`/endsession` - ends an active session\n`/resetsession` - reset an active session\n`/link` - link your hypixel account\n`/unlink` - unlink your hypixel account\n`/prestige` - view stats at specified stars\n`/shop` - view any players shop layout\n`/mostplayed` - view most played stats\n`/bedwars` - view total bedwars stats\n`/average` - view average bedwars stats\n`/resources` - view resource stats and info\n`/skin` - view or download and player's skin\n`/practice` - view practice modes stats\n`/milestones` - view milestone calculations", inline=False)
    embed_var.add_field(name='About Us', value=f'{NAME} aims to revive features of an assumed discontinued bot and bring its own unique features to the table. {NAME} offers a blend of old and new functionality to provide a comprehensive experience for Bedwars players.\nFor any questions, bugs or concerns, contact us on our [discord](https://discord.gg/rHmHZ9vvwE).', inline=False)
    await interaction.response.send_message(embed=embed_var)


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
    try:
        name, uuid = await authenticate_user(username, interaction)
    except Exception:
        await interaction.response.send_message("That player doesn't exist!")
        return
    if session is None:
        session = 1
    refined = name.replace('_', r'\_')
    with sqlite3.connect(f'{os.getcwd()}/database/sessions.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM sessions WHERE session=? AND uuid=?", (session, uuid))
        sessionstats = cursor.fetchone()
        cursor.execute(f"SELECT * FROM sessions WHERE uuid='{uuid}'")
        any_session = cursor.fetchone()
    if sessionstats:
        await interaction.response.send_message('Generating please wait <a:loading1:1062561739989860462>')
        interid = await interaction.original_response()
        os.makedirs(f'{os.getcwd()}/database/activerenders/{interid.id}')
        skin_res = requests.get(f'https://visage.surgeplay.com/bust/144/{uuid}', timeout=10)

        hypixel_data = get_hypixel_data(uuid)
        try:
            current_star = renderprojection(name, uuid, session, mode="Overall", target=prestige, hypixel_data=hypixel_data, skin_res=skin_res.content, save_dir=interid.id)
        except ZeroDivisionError:
            content = f"Dude thats literally the same star that {refined} already is!\nUnless maybe an error occured? In which case please report this to the developers!"
            await interaction.edit_original_response(content=content)
            return
        view = SelectView(name, user=interaction.user.id, interid=interid, inter=interaction, mode='Select a mode')

        content = ":warning: THE LEVEL YOU ENTERED IS LOWER THAN THE CURRENT STAR! :warning:" if current_star > prestige else None
        await interaction.edit_original_response(content=content, attachments=[discord.File(f"{os.getcwd()}/database/activerenders/{interid.id}/overall.png")], view=view)
        renderprojection(name, uuid, session, mode="Solos", target=prestige, hypixel_data=hypixel_data, skin_res=skin_res.content, save_dir=interid.id)
        renderprojection(name, uuid, session, mode="Doubles", target=prestige, hypixel_data=hypixel_data, skin_res=skin_res.content, save_dir=interid.id)
        renderprojection(name, uuid, session, mode="Threes", target=prestige, hypixel_data=hypixel_data, skin_res=skin_res.content, save_dir=interid.id)
        renderprojection(name, uuid, session, mode="Fours", target=prestige, hypixel_data=hypixel_data, skin_res=skin_res.content, save_dir=interid.id)
    else:
        if not any_session:
            await interaction.response.defer()
            returnvalue = reqapi.startsession(uuid, session=1)
            if returnvalue is True:
                await interaction.followup.send(f"**{refined}** has no active sessions so one was created!")
            else:
                await interaction.followup.send(f"{refined} has never played before!")
        else:
            await interaction.response.send_message(f"{refined} doesn't have an active session with ID: `{session}`!")

# Shopkeeper
@client.tree.command(name = "shop", description = "View the shopkeeper of a player")
@app_commands.autocomplete(username=username_autocompletion)
@app_commands.describe(username='The player you want to view')
@app_commands.checks.dynamic_cooldown(check_subscription)
async def shop(interaction: discord.Interaction,username: str=None):
    try:
        name, uuid = await authenticate_user(username, interaction)
    except Exception:
        await interaction.response.send_message("That player doesn't exist!")
        return
    refined = name.replace('_', r'\_')
    await interaction.response.send_message('Generating please wait <a:loading1:1062561739989860462>')

    rendered = rendershop(uuid)
    if rendered is not False:
        await interaction.edit_original_response(content=None, attachments=[discord.File(rendered, filename="shop.png")])
    else:
        await interaction.edit_original_response(content=f'**{refined} has not played before!**')

# Most Played
@client.tree.command(name = "mostplayed", description = "Most played mode of a player")
@app_commands.autocomplete(username=username_autocompletion)
@app_commands.describe(username='The player you want to view')
@app_commands.checks.dynamic_cooldown(check_subscription)
async def most_played(interaction: discord.Interaction,username: str=None):
    try:
        name, uuid = await authenticate_user(username, interaction)
    except Exception:
        await interaction.response.send_message("That player doesn't exist!")
        return
    await interaction.response.send_message('Generating please wait <a:loading1:1062561739989860462>')

    rendered = rendergraph(name, uuid)
    await interaction.edit_original_response(content=None, attachments=[discord.File(rendered, filename='mostplayed.png')])

# Suggest
class SubmitSuggestion(ui.Modal, title='Submit Suggestion'):
    suggestion = ui.TextInput(label='Suggestion:', placeholder='You should add...', style=discord.TextStyle.long)

    async def on_submit(self, interaction: discord.Interaction):
        channel = client.get_channel(1065918528236040232)
        submit_embed = discord.Embed(title=f'Suggestion by {interaction.user} ({interaction.user.id})', description=f'**Suggestion:**\n{self.suggestion}', color=0x55FFC8)
        await channel.send(embed=submit_embed)
        await interaction.response.send_message('Successfully submitted suggestion!', ephemeral=True)

@client.tree.command(name='suggest', description='Suggest a feature you would like to see added!')
async def suggest(interaction: discord.Interaction):
    await interaction.response.send_modal(SubmitSuggestion())

# Total stats
@client.tree.command(name = "bedwars", description = "View the general stats of a player")
@app_commands.autocomplete(username=username_autocompletion)
@app_commands.describe(username='The player you want to view')
@app_commands.checks.dynamic_cooldown(check_subscription)
async def total(interaction: discord.Interaction, username: str=None):
    try:
        name, uuid = await authenticate_user(username, interaction)
    except Exception:
        await interaction.response.send_message("That player doesn't exist!")
        return
    await interaction.response.send_message('Generating please wait <a:loading1:1062561739989860462>')
    interid = await interaction.original_response()

    os.makedirs(f'{os.getcwd()}/database/activerenders/{interid.id}')
    skin_res = requests.get(f'https://visage.surgeplay.com/bust/144/{uuid}', timeout=10)
    hypixel_data = get_hypixel_data(uuid)


    rendertotal(name, uuid, mode="Overall", hypixel_data=hypixel_data, skin_res=skin_res.content, save_dir=interid.id, method="generic")
    view = SelectView(name, user=interaction.user.id, interid=interid, inter=interaction, mode='Select a mode')
    await interaction.edit_original_response(content=None, attachments=[discord.File(f"{os.getcwd()}/database/activerenders/{interid.id}/overall.png")], view=view)
    rendertotal(name, uuid, mode="Solos", hypixel_data=hypixel_data, skin_res=skin_res.content, save_dir=interid.id, method="generic")
    rendertotal(name, uuid, mode="Doubles", hypixel_data=hypixel_data, skin_res=skin_res.content, save_dir=interid.id, method="generic")
    rendertotal(name, uuid, mode="Threes", hypixel_data=hypixel_data, skin_res=skin_res.content, save_dir=interid.id, method="generic")
    rendertotal(name, uuid, mode="Fours", hypixel_data=hypixel_data, skin_res=skin_res.content, save_dir=interid.id, method="generic")


# Ratio Stats
@client.tree.command(name = "average", description = "View the average stats of a player")
@app_commands.autocomplete(username=username_autocompletion)
@app_commands.describe(username='The player you want to view')
@app_commands.checks.dynamic_cooldown(check_subscription)
async def average(interaction: discord.Interaction, username: str=None):
    try:
        name, uuid = await authenticate_user(username, interaction)
    except Exception:
        await interaction.response.send_message("That player doesn't exist!")
        return
    await interaction.response.send_message('Generating please wait <a:loading1:1062561739989860462>')
    interid = await interaction.original_response()

    os.makedirs(f'{os.getcwd()}/database/activerenders/{interid.id}')
    hypixel_data = get_hypixel_data(uuid)

    renderratio(name, uuid, mode="Overall", hypixel_data=hypixel_data, save_dir=interid.id)
    view = SelectView(name, user=interaction.user.id, interid=interid, inter=interaction, mode='Select a mode')
    await interaction.edit_original_response(content=None, attachments=[discord.File(f"{os.getcwd()}/database/activerenders/{interid.id}/overall.png")], view=view)
    renderratio(name, uuid, mode="Solos", hypixel_data=hypixel_data, save_dir=interid.id)
    renderratio(name, uuid, mode="Doubles", hypixel_data=hypixel_data, save_dir=interid.id)
    renderratio(name, uuid, mode="Threes", hypixel_data=hypixel_data, save_dir=interid.id)
    renderratio(name, uuid, mode="Fours", hypixel_data=hypixel_data, save_dir=interid.id)

# Resources Stats
@client.tree.command(name = "resources", description = "View the resource stats of a player")
@app_commands.autocomplete(username=username_autocompletion)
@app_commands.describe(username='The player you want to view')
@app_commands.checks.dynamic_cooldown(check_subscription)
async def resources(interaction: discord.Interaction, username: str=None):
    try:
        name, uuid = await authenticate_user(username, interaction)
    except Exception:
        await interaction.response.send_message("That player doesn't exist!")
        return
    await interaction.response.send_message('Generating please wait <a:loading1:1062561739989860462>')
    interid = await interaction.original_response()

    os.makedirs(f'{os.getcwd()}/database/activerenders/{interid.id}')
    hypixel_data = get_hypixel_data(uuid)

    renderresources(name, uuid, mode="Overall", hypixel_data=hypixel_data, save_dir=interid.id)
    view = SelectView(name, user=interaction.user.id, interid=interid, inter=interaction, mode='Select a mode')
    await interaction.edit_original_response(content=None, attachments=[discord.File(f"{os.getcwd()}/database/activerenders/{interid.id}/overall.png")], view=view)
    renderresources(name, uuid, mode="Solos", hypixel_data=hypixel_data, save_dir=interid.id)
    renderresources(name, uuid, mode="Doubles", hypixel_data=hypixel_data, save_dir=interid.id)
    renderresources(name, uuid, mode="Threes", hypixel_data=hypixel_data, save_dir=interid.id)
    renderresources(name, uuid, mode="Fours", hypixel_data=hypixel_data, save_dir=interid.id)


# Skin View
@client.tree.command(name = "skin", description = "View the skin of a player")
@app_commands.autocomplete(username=username_autocompletion)
@app_commands.describe(username='The player you want to view')
@app_commands.checks.dynamic_cooldown(check_subscription)
async def skin(interaction: discord.Interaction, username: str=None):
    try:
        name, uuid = await authenticate_user(username, interaction)
    except Exception:
        await interaction.response.send_message("That player doesn't exist!")
        return
    refined = name.replace('_', r'\_')
    image_bytes = requests.get(f'https://visage.surgeplay.com/full/{uuid}', timeout=10).content
    file = discord.File(BytesIO(image_bytes), filename='skin.png')
    embed = discord.Embed()
    embed.set_image(url="attachment://skin.png")

    skin_embed = discord.Embed(title=f"{refined}'s skin",url= f"https://namemc.com/profile/{uuid}", description=f"[Click here](https://crafatar.com/skins/{uuid}) to download", color=0x00AFF4)
    skin_embed.set_image(url="attachment://skin.png")
    await interaction.response.send_message(file=file, embed=skin_embed)


# Practice Stats
@client.tree.command(name = "practice", description = "View the practice stats of a player")
@app_commands.autocomplete(username=username_autocompletion)
@app_commands.describe(username='The player you want to view')
@app_commands.checks.dynamic_cooldown(check_subscription)
async def practice(interaction: discord.Interaction, username: str=None):
    try:
        name, uuid = await authenticate_user(username, interaction)
    except Exception:
        await interaction.response.send_message("That player doesn't exist!")
        return
    await interaction.response.send_message('Generating please wait <a:loading1:1062561739989860462>')

    rendered = renderpractice(name, uuid)
    await interaction.edit_original_response(content=None, attachments=[discord.File(rendered, filename='practice.png')])


# Milestone Stats
@client.tree.command(name = "milestones", description = "View the milestone stats of a player")
@app_commands.autocomplete(username=username_autocompletion)
@app_commands.describe(username='The player you want to view')
@app_commands.checks.dynamic_cooldown(check_subscription)
async def milestones(interaction: discord.Interaction, username: str=None):
    try:
        name, uuid = await authenticate_user(username, interaction)
    except Exception:
        await interaction.response.send_message("That player doesn't exist!")
        return
    await interaction.response.send_message('Generating please wait <a:loading1:1062561739989860462>')
    interid = await interaction.original_response()
    os.makedirs(f'{os.getcwd()}/database/activerenders/{interid.id}')

    hypixel_data = get_hypixel_data(uuid)
    rendermilestones(name, uuid, mode="Overall", hypixel_data=hypixel_data, save_dir=interid.id)
    view = SelectView(name, user=interaction.user.id, interid=interid, inter=interaction, mode='Select a mode')
    await interaction.edit_original_response(content=None, attachments=[discord.File(f"{os.getcwd()}/database/activerenders/{interid.id}/overall.png")], view=view)
    rendermilestones(name, uuid, mode="Solos", hypixel_data=hypixel_data, save_dir=interid.id)
    rendermilestones(name, uuid, mode="Doubles", hypixel_data=hypixel_data, save_dir=interid.id)
    rendermilestones(name, uuid, mode="Threes", hypixel_data=hypixel_data, save_dir=interid.id)
    rendermilestones(name, uuid, mode="Fours", hypixel_data=hypixel_data, save_dir=interid.id)


# Active Cosmetics
@client.tree.command(name = "activecosmetics", description = "View the practice stats of a player")
@app_commands.autocomplete(username=username_autocompletion)
@app_commands.describe(username='The player you want to view')
@app_commands.checks.dynamic_cooldown(check_subscription)
async def active_cosmetics(interaction: discord.Interaction, username: str=None):
    try:
        name, uuid = await authenticate_user(username, interaction)
    except Exception:
        await interaction.response.send_message("That player doesn't exist!")
        return
    await interaction.response.send_message('Generating please wait <a:loading1:1062561739989860462>')

    rendered = rendercosmetics(name, uuid)
    await interaction.edit_original_response(content=None, attachments=[discord.File(rendered, filename='cosmetics.png')])


# Hotbar
@client.tree.command(name = "hotbar", description = "View the hotbar preferences of a player")
@app_commands.autocomplete(username=username_autocompletion)
@app_commands.describe(username='The player you want to view')
@app_commands.checks.dynamic_cooldown(check_subscription)
async def hotbar(interaction: discord.Interaction,username: str=None):
    try:
        name, uuid = await authenticate_user(username, interaction)
    except Exception:
        await interaction.response.send_message("That player doesn't exist!")
        return
    refined = name.replace('_', r'\_')
    await interaction.response.send_message('Generating please wait <a:loading1:1062561739989860462>')

    rendered = renderhotbar(name, uuid)
    if rendered is not False:
        await interaction.edit_original_response(content=None, attachments=[discord.File(rendered, filename="hotbar.png")])
    else:
        await interaction.edit_original_response(content=f'**{refined} does not have a hotbar set!**')

# Pointless stats
@client.tree.command(name = "pointless", description = "View the general pointless stats of a player")
@app_commands.autocomplete(username=username_autocompletion)
@app_commands.describe(username='The player you want to view')
@app_commands.checks.dynamic_cooldown(check_subscription)
async def pointless(interaction: discord.Interaction, username: str=None):
    try:
        name, uuid = await authenticate_user(username, interaction)
    except Exception:
        await interaction.response.send_message("That player doesn't exist!")
        return
    await interaction.response.send_message('Generating please wait <a:loading1:1062561739989860462>')
    interid = await interaction.original_response()

    os.makedirs(f'{os.getcwd()}/database/activerenders/{interid.id}')
    skin_res = requests.get(f'https://visage.surgeplay.com/bust/144/{uuid}', timeout=10)
    hypixel_data = get_hypixel_data(uuid)


    rendertotal(name, uuid, mode="Overall", hypixel_data=hypixel_data, skin_res=skin_res.content, save_dir=interid.id, method="pointless")
    view = SelectView(name, user=interaction.user.id, interid=interid, inter=interaction, mode='Select a mode')
    await interaction.edit_original_response(content=None, attachments=[discord.File(f"{os.getcwd()}/database/activerenders/{interid.id}/overall.png")], view=view)
    rendertotal(name, uuid, mode="Solos", hypixel_data=hypixel_data, skin_res=skin_res.content, save_dir=interid.id, method="pointless")
    rendertotal(name, uuid, mode="Doubles", hypixel_data=hypixel_data, skin_res=skin_res.content, save_dir=interid.id, method="pointless")
    rendertotal(name, uuid, mode="Threes", hypixel_data=hypixel_data, skin_res=skin_res.content, save_dir=interid.id, method="pointless")
    rendertotal(name, uuid, mode="Fours", hypixel_data=hypixel_data, skin_res=skin_res.content, save_dir=interid.id, method="pointless")

client.run(TOKEN)
