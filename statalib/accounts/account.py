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
from ..functions import db_connect


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

    def load(self, create: bool=True) -> AccountData | None:
        """
        Load the account from the database.

        :param create: Whether to create and return the account if it doesn't exist.
        :return AccountData | None: The account data, or None if it doesn't exist.
        """
        with db_connect() as conn:
            cursor = conn.cursor()

            account_data = self._select_account_data(cursor)

            if account_data is None:
                if create is False:
                    return None

                self.create()
                return self.load(create=False)

        self.__exists = True
        return AccountData.new(account_data)

    def create(
        self,
        creation_timestamp: float | None=None,
        permissions: list[str] | None=None,
        blacklisted: bool=False,
        account_id: int | None=None,
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
            account_id
        )
        self.__exists = True

    def update(self, blacklisted: bool, create: bool=True) -> None:
        """
        Update the account's metadata such as blacklist standing.

        :param blacklisted: Whether the account should be blacklisted.
        :param create: Whether to create the account if it doesn't exist.
        """
        account_data = self.load()

        if not account_data:
            if create:
                self.create(blacklisted=blacklisted)
            return

        with db_connect() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'UPDATE accounts SET blacklisted = ? WHERE discord_id = ?',
                (int(blacklisted), self._discord_user_id,))

        self.__exists = True

    def delete(self) -> None:
        """
        Delete the account from the database.
        This will not delete data in other tables such as voting data and themes.
        """
        with db_connect() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'DELETE FROM accounts WHERE discord_id = ?', (self._discord_user_id,))

        self.__exists = False

    @property
    def exists(self) -> bool:
        """Whether the account exists in the database."""
        if self.__exists is None:
            self.__exists = self.load(create=False) is not None
        return self.__exists
