"""Standalone account related functions."""

import sqlite3
from datetime import UTC, datetime
from typing import NamedTuple

from .common import REL_PATH


class AccountDataTuple(NamedTuple):
    """Named tuple for account data."""
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
    Create a new account for a user if ones doesn't already exist.

    :param discord_id: The Discord user ID of the respective user.
    :param account_id: Overrides the default autoincrement account ID.
    :param creation_timestamp: Overrides the default creation timestamp \
        of the account.
    :param permissions: Set the user's initial permissions.
    :param blacklisted: Set whether the account is initially blacklisted.
    :param cursor: A custom `sqlite3.Cursor` object to operate on.
    """
    if creation_timestamp is None:
        creation_timestamp = datetime.now(UTC).timestamp()

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
    Retreive the account data for a user.

    :param discord_id: The Discord user ID of the user.
    :param create: Whether to create an account if one does not already exist.
    :param cursor: A custom `sqlite3.Cursor` object to operate on.
    :return AccountDataTuple | None: The account data for the user.
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
) -> None:
    """
    Blacklist or unblacklist an account.

    :param discord_id: The Discord user ID of the user.
    :param blacklisted: Whether the user should be blacklisted.
    :param create: Whether to create an account if one does not already exist.
    :param cursor: A custom `sqlite3.Cursor` object to operate on.
    """
    if cursor:
        _set_account_blacklist(discord_id, blacklisted, create, cursor)
        return

    with sqlite3.connect(f'{REL_PATH}/database/core.db') as conn:
        cursor = conn.cursor()
        _set_account_blacklist(discord_id, blacklisted, create, cursor)
