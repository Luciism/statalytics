import sqlite3
import typing

from discord import app_commands, Interaction

from .functions import REL_PATH
from .linking import get_linked_player
from .mcfetch import FetchPlayer


async def session_autocompletion(
    interaction: Interaction,
    current: str
) -> typing.List[app_commands.Choice[str]]:
    """
    Interaction session autocomplete\n
    Dynamic to username field
    """
    username = None
    for option in interaction.data.get('options', []):
        # Check if the current option is the top-level 'username' option
        if option.get('name') == 'username':
            username = option.get('value')
            break
        # If the current option has nested options
        if option.get('options'):
            for option2 in option['options']:
                # Check if any of the nested options is the 'username' option
                if option2.get('name') == 'username':
                    username = option2.get('value')
                    break
            if username:
                break

    if username:
        try:
            uuid: str = FetchPlayer(name=username).uuid
        except KeyError:
            return []
    else:
        uuid = get_linked_player(interaction.user.id)
        if not uuid:
            return []

    with sqlite3.connect(f'{REL_PATH}/database/core.db') as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM sessions WHERE uuid='{uuid}'")
        sessions = cursor.fetchall()

    data = [app_commands.Choice(name=ses[0], value=ses[0]) for ses in sessions]
    return data


async def username_autocompletion(
    interaction: Interaction,
    current: str
) -> typing.List[app_commands.Choice[str]]:
    """
    Interaction username autocomplete
    """
    with sqlite3.connect(f'{REL_PATH}/database/core.db') as conn:
        cursor = conn.cursor()
        result = cursor.execute(
            "SELECT * FROM autofill WHERE LOWER(username) LIKE ? LIMIT 25",
            (fr'%{current.lower()}%',)
        )

    data = [app_commands.Choice(name=row[2], value=row[2]) for row in result]
    return data
