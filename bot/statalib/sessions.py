import sqlite3
from datetime import datetime

import discord

from .errors import SessionNotFoundError
from .calctools import get_player_dict
from .discord_utils.responses import interaction_send_object
from .network import fetch_hypixel_data
from .functions import (
    get_config,
    fname,
    REL_PATH
)


async def start_session(uuid: str, session: int,
                        hypixel_data: dict | None = None) -> None:
    """
    Initiate a bedwars stats session
    :param uuid: The uuid of the player to initiate a session for
    :param session: The id of the session being initiated
    :param hypixel_data: pass in optional custom hypixel data
    """
    if not hypixel_data:
        hypixel_data = await fetch_hypixel_data(uuid, cache=False)
    hypixel_data = get_player_dict(hypixel_data)

    stat_keys = get_config()['tracked_bedwars_stats']

    stat_values = {
        "session": session,
        "uuid": uuid,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "level": hypixel_data.get("achievements", {}).get("bedwars_level", 0),
    }

    for key in stat_keys:
        stat_values[key] = hypixel_data.get("stats", {}).get("Bedwars", {}).get(key, 0)

    with sqlite3.connect(f'{REL_PATH}/database/core.db') as conn:
        cursor = conn.cursor()

        cursor.execute("SELECT uuid FROM sessions WHERE session=? AND uuid=?", (session, uuid))
        row: tuple = cursor.fetchone()

        if not row:
            columns = ', '.join(stat_values.keys())
            question_marks = ', '.join('?'*len(stat_values.values()))
            query = f"INSERT INTO sessions ({columns}) VALUES ({question_marks})"
            cursor.execute(query, tuple(stat_values.values()))
        else:
            set_clause = ', '.join([f"{column} = ?" for column in stat_values])
            query = f"UPDATE sessions SET {set_clause} WHERE session=? AND uuid=?"
            values = list(stat_values.values()) + [session, uuid]
            cursor.execute(query, tuple(values))


def _find_dynamic_session(uuid: str, session: int | None=None) -> tuple | None:
    """
    Returns a session based on the provided session\n
    if a session is not provided, a session with the lowest id will be used
    :param uuid: The uuid of the session owner
    :param session: The session to attempt to be retrieved
    """
    with sqlite3.connect(f'{REL_PATH}/database/core.db') as conn:
        cursor = conn.cursor()

        if session:
            cursor.execute(
                "SELECT session FROM sessions WHERE session = ? AND uuid = ?", (session, uuid))
        else:
            cursor.execute(
                "SELECT session FROM sessions WHERE uuid = ? ORDER BY session ASC", (uuid,))
        session_data: tuple = cursor.fetchone()

    return session_data[0] if session_data else None


async def find_dynamic_session(interaction: discord.Interaction, username: str,
                            uuid: str, session: int | None=None, eph=True) -> tuple | bool:
    """
    Dynamically gets a session of a user\n
    If session is 100, the first session to exist will be returned
    :param interaction: The discord interaction object used
    :param username: The username of the session owner
    :param uuid: The uuid of the session owner
    :param session: The session to attempt to be retrieved
    :param eph: whether or not to respond ephemerally
    """
    returned_session = _find_dynamic_session(uuid, session)
    respond = interaction_send_object(interaction)

    # no sessions exist because... i forgot to finish this comment now idk
    if not returned_session and not session:
        await start_session(uuid, session=1)
        await respond(
            f"**{fname(username)}** has no active sessions so one was created!",
            ephemeral=eph
        )
        raise SessionNotFoundError

    if not returned_session:
        await respond(
            f"**{fname(username)}** doesn't have an active session with ID: `{session}`!",
            ephemeral=eph
        )
        raise SessionNotFoundError

    return returned_session
