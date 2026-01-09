"""Private shared utility for creating accounts."""

import sqlite3
from datetime import datetime, UTC

from ..usage import insert_growth_data
from ..db import ensure_cursor


@ensure_cursor
def create_account(
    discord_user_id: int,
    creation_timestamp: float | None=None,
    permissions: list[str] | None=None,
    blacklisted: bool=False,
    account_id: int | None=None,
    *, cursor: sqlite3.Cursor=None
) -> None:
    """Create an account in the database if it doesn't exist."""
    existing_row = cursor.execute(
        "SELECT account_id FROM accounts WHERE discord_id = ?", [discord_user_id]
    ).fetchone()

    if existing_row is not None:
        return  # Account exists

    if creation_timestamp is None:
        creation_timestamp = datetime.now(UTC).timestamp()

    account_data = {
        "discord_id": discord_user_id,
        "creation_timestamp": creation_timestamp,
        "permissions": ','.join(permissions or []),
        "blacklisted": int(blacklisted)
    }
    # Add account ID if provided, otherwise let it autoincrement.
    if account_id is not None:
        account_data["account_id"] = account_id

    # Build the query based off of the account data dict.
    column_names = ', '.join(account_data.keys())
    question_marks = ', '.join('?'*len(account_data.keys()))

    _ = cursor.execute(
        f'INSERT INTO accounts ({column_names}) VALUES ({question_marks})',
        tuple(account_data.values())
    )
 
    insert_growth_data(discord_user_id, action='add', growth='user', cursor=cursor)

