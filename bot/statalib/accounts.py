import sqlite3
from datetime import datetime
from typing import NamedTuple

from .functions import REL_PATH


class AccountDataTuple(NamedTuple):
    """Account data named tuple"""
    account_id: int
    discord_id: int
    creation_timestamp: float
    permissions: str
    blacklisted: int


def create_account(
    discord_id: int,
    account_id: int=None,
    creation_timestamp: float=None,
    permissions: list | str=None,
    blacklisted: bool=False,
    cursor: sqlite3.Cursor=None
) -> None:
    """
    Creates a new account for a user if ones doesn't already exist
    :param discord_id: the discord id of the respective user
    :param account_id: override the autoincrement account id
    :param creation_timestamp: override the creation timestamp of the account
    :param permissions: set the permissions for the user
    :param blacklisted: set whether the accounts is blacklisted
    :param cursor: custom `sqlite3.Cursor` object to insert the account data with
    """
    if creation_timestamp is None:
        creation_timestamp = datetime.utcnow().timestamp()

    data = {
        'discord_id': discord_id,
        'creation_timestamp': creation_timestamp,
        'blacklisted': int(blacklisted)
    }

    if account_id:
        data['account_id'] = account_id

    if permissions:
        if isinstance(permissions, list):
            permissions = ','.join(permissions)
        data['permissions'] = permissions

    column_names = ', '.join(data.keys())
    question_marks = ', '.join('?'*len(data.keys()))

    query = (
        'INSERT OR IGNORE INTO accounts '
        f'({column_names}) VALUES ({question_marks})', tuple(data.values()))

    if cursor:
        cursor.execute(*query)
        return

    with sqlite3.connect(f'{REL_PATH}/database/core.db') as conn:
        cursor = conn.cursor()
        cursor.execute(*query)


def _select_account_data(discord_id: int, cursor: sqlite3.Cursor):
    cursor.execute(
        'SELECT * FROM accounts WHERE discord_id = ?', (discord_id,))
    return cursor.fetchone()


def _get_account(
    discord_id: int,
    create: bool,
    cursor: sqlite3.Cursor,
) -> AccountDataTuple | None:
    account_data = _select_account_data(discord_id, cursor)

    if account_data is None:
        if not create:
            return None

        create_account(discord_id, cursor=cursor)
        account_data = _select_account_data(discord_id, cursor)

    return AccountDataTuple(*account_data)


def get_account(
    discord_id: int,
    create: bool=False,
    cursor: sqlite3.Cursor=None
) -> AccountDataTuple | None:
    """
    Gets the account data for a user
    :param discord_id: the discord id of the user to get the account data for
    :param create: if an account should be created if one does not already exists
    :param cursor: custom `sqlite3.Cursor` object to execute queries with
    """
    if cursor:
        return _get_account(discord_id, create, cursor)

    with sqlite3.connect(f'{REL_PATH}/database/core.db') as conn:
        cursor = conn.cursor()
        return _get_account(discord_id, create, cursor)


def _set_account_blacklist(
    discord_id: int,
    blacklisted: bool,
    create: bool,
    cursor: sqlite3.Cursor
):
    account_data = _select_account_data(discord_id, cursor=cursor)
    if not account_data:
        if create:
            create_account(discord_id, blacklisted=blacklisted, cursor=cursor)
        return

    cursor.execute(
        'UPDATE accounts SET blacklisted = ? WHERE discord_id = ?',
        (int(blacklisted), discord_id,))


def set_account_blacklist(
    discord_id: int,
    blacklisted: bool=True,
    create: bool=True,
    cursor: sqlite3.Cursor=None
):
    """
    Set the blacklist property of an account
    :param discord_id: the discord id of the user account
    to modify the blacklist of
    :param blacklisted: whether to blacklist or unblacklist the user
    :param create: whether or not to create the account if it doesn't exist
    :param cursor: custom `sqlite3.Cursor` object to execute queries with
    """
    if cursor:
        _set_account_blacklist(discord_id, blacklisted, create, cursor)
        return

    with sqlite3.connect(f'{REL_PATH}/database/core.db') as conn:
        cursor = conn.cursor()
        _set_account_blacklist(discord_id, blacklisted, create, cursor)
