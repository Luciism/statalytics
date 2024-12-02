"""Application command autocompletion functions."""

from discord import app_commands, Interaction

import statalib as lib
from statalib.accounts import AccountLinking


async def session_autocompletion(
    interaction: Interaction,
    current: str
) -> list[app_commands.Choice[str]]:
    """Session autocomplete that is dynamic to the player field."""
    username = None
    for option in interaction.data.get('options', []):
        # Check if the current option is the top-level 'player' option
        if option.get('name') == 'player':
            username = option.get('value')
            break
        # If the current option has nested options
        if option.get('options'):
            for option2 in option['options']:
                # Check if any of the nested options is the 'player' option
                if option2.get('name') == 'player':
                    username = option2.get('value')
                    break
            if username:
                break

    if username:
        uuid = await lib.mcfetch.AsyncFetchPlayer(name=username).uuid
    else:
        uuid = AccountLinking(interaction.user.id).get_linked_player_uuid()

    if uuid is None:
        return []

    active_sessions = lib.sessions.SessionManager(uuid).active_sessions()

    data = [app_commands.Choice(name=ses, value=ses) for ses in active_sessions]
    return data


async def username_autocompletion(
    interaction: Interaction,
    current: str
) -> list[app_commands.Choice[str]]:
    """Username autocomplete."""
    with lib.db_connect() as conn:
        cursor = conn.cursor()
        result = cursor.execute(
            "SELECT * FROM autofill WHERE LOWER(username) LIKE ? LIMIT 25",
            (fr'%{current.lower()}%',)
        )

    data = [app_commands.Choice(name=row[2], value=row[2]) for row in result]
    return data
