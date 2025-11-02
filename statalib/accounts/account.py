"""Main account classes."""

import sqlite3
from dataclasses import dataclass
from datetime import datetime, UTC

from ._create import create_account
from .permissions import AccountPermissions
from .themes import AccountThemes
from .subscriptions import AccountSubscriptions
from .linking import AccountLinking
from .voting import AccountVoting
from .usage import AccountUsage
from ..db import ensure_cursor


@ensure_cursor
def autocomplete_discord_ids(
    query: str,
    result_limit: int=10,
    *, cursor: sqlite3.Cursor=None
) -> list[int]:
    """
    Retrieve a list of Discord IDs that match the given query.

    :param query: The query to search for Discord IDs.
    :param result_limit: The maximum number of results to return.
    :return list: A list of Discord IDs that match the query.
    """
    rows: list[tuple[int]] = cursor.execute(
        'SELECT discord_id FROM accounts WHERE discord_id LIKE ? LIMIT ?',
        (fr'%{query}%', result_limit)
    ).fetchall()

    return [row[0] for row in rows]


@dataclass
class AccountData:
    """Account data dataclass."""
    account_id: int
    """The account's locally assigned ID (not Discord ID)."""
    discord_id: int
    """The Discord user ID associated with the account."""
    creation_timestamp: float
    """The account's creation timestamp."""
    permissions: list[str]
    """The account's permissions."""
    blacklisted: bool
    """Whether the account is blacklisted."""

    @staticmethod
    def new(account_data: tuple) -> 'AccountData':
        """Create a new account data object."""
        return AccountData(
            account_data[0],  # Account ID
            account_data[1],  # Discord user ID
            account_data[2],  # Creation timestamp
            [perm for perm in (account_data[3] or '').split(',') if perm],  # Permissions
            account_data[4]  # Blacklist standing
        )

    @property
    def formatted_creation_date(self) -> str:
        """The formatted creation date of the account (%d/%m/%Y)."""
        creation_dt = datetime.fromtimestamp(self.creation_timestamp, UTC)
        return creation_dt.strftime('%d/%m/%Y')

    def as_dict(self) -> dict:
        return {
            'account_id': self.account_id,
            'discord_id': self.discord_id,
            'creation_timestamp': self.creation_timestamp,
            'formatted_creation_date': self.formatted_creation_date,
            'permissions': self.permissions,
            'blacklisted': self.blacklisted
        }


class Account:
    """Represent a user's account."""
    def __init__(self, discord_user_id: int) -> None:
        self._discord_user_id = discord_user_id
        self.__exists = None

        self.permissions = AccountPermissions(discord_user_id)
        "A permission manager for the account."

        self.themes = AccountThemes(discord_user_id)
        "A theme manager for the account."

        self.subscriptions = AccountSubscriptions(discord_user_id)
        "A subscription manager for the account."

        self.linking = AccountLinking(discord_user_id)
        "A linking manager for the account."

        self.voting = AccountVoting(discord_user_id)
        "A voting manager for the account."

        self.usage = AccountUsage(discord_user_id)
        "A usage manager for the account."

    def _select_account_data(self, cursor: sqlite3.Cursor) -> tuple:
        return cursor.execute(
            'SELECT * FROM accounts WHERE discord_id = ?', (self._discord_user_id,)
        ).fetchone()

    @ensure_cursor
    def load(
        self,
        create: bool=True,
        *, cursor: sqlite3.Cursor=None
    ) -> AccountData | None:
        """
        Load the account from the database.

        :param create: Whether to create and return the account if it doesn't exist.
        :return AccountData | None: The account data, or None if it doesn't exist.
        """
        account_data = self._select_account_data(cursor)

        if account_data is None:
            if create is False:
                return None

            self.create(cursor=cursor)
            return self.load(create=False, cursor=cursor)

        self.__exists = True
        return AccountData.new(account_data)

    @ensure_cursor
    def create(
        self,
        creation_timestamp: float | None=None,
        permissions: list[str] | None=None,
        blacklisted: bool=False,
        account_id: int | None=None,
        *, cursor: sqlite3.Cursor=None
    ) -> None:
        """
        Create the account if it doesn't already exist. If the account already
        exists, this function does nothing.

        :param creation_timestamp: Specify a custom creation timestamp.
        :param permissions: A list of initial permissions to set for the account.
        :param blacklist: Whether the account should be initially blacklisted.
        :param account_id: Specify a custom account ID, otherwise one will be \
            autoincremented.
        """
        create_account(
            self._discord_user_id,
            creation_timestamp,
            permissions,
            blacklisted,
            account_id,
            cursor=cursor
        )
        self.__exists = True

    @ensure_cursor
    def update(
        self,
        blacklisted: bool | None=None,
        creation_timestamp: float | None=None,
        account_id: int | None=None,
        create: bool=True,
        *, cursor: sqlite3.Cursor=None
    ) -> None:
        """
        Update the account's metadata such as blacklist standing.

        :param blacklisted: Whether the account should be blacklisted.
        :param create: Whether to create the account if it doesn't exist.
        """
        account_data = self.load(cursor=cursor, create=False)

        if not account_data:
            if create:
                self.create(
                    creation_timestamp=creation_timestamp,
                    account_id=account_id,
                    blacklisted=blacklisted,
                    cursor=cursor)
            return

        update_data = {}

        if blacklisted is not None:
            update_data['blacklisted'] = blacklisted
        if creation_timestamp is not None:
            update_data['creation_timestamp'] = creation_timestamp
        if account_id is not None:
            update_data['account_id'] = account_id

        set_statement = ', '.join([f'{key} = ?' for key in update_data])
        cursor.execute(
            f'UPDATE accounts SET {set_statement} WHERE discord_id = ?',
            (*update_data.values(), self._discord_user_id,))

        self.__exists = True

    @ensure_cursor
    def delete(self, *, cursor: sqlite3.Cursor=None) -> None:
        """
        Delete the account from the database.
        This will not delete data in other tables such as voting data and themes.
        """
        cursor.execute(
            'DELETE FROM accounts WHERE discord_id = ?', (self._discord_user_id,))

        self.__exists = False

    @property
    def exists(self) -> bool:
        """Whether the account exists in the database."""
        if self.__exists is None:
            self.__exists = self.load(create=False) is not None
        return self.__exists
