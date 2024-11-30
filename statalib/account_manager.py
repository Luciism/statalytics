"""Provides an all-in-one `Account` class for managing accounts."""

from datetime import UTC, datetime

from .mcfetch import FetchPlayer2
from .accounts import get_account, set_account_blacklist, create_account
from .functions import comma_separated_to_list, get_voting_data, commands_ran
from .linking import LinkingManager, get_linked_player
from .permissions import PermissionManager, has_access, has_permission
from .subscriptions import SubscriptionManager, Subscription
from .themes import (
    ThemeManager, get_owned_themes, get_active_theme, get_voter_themes)


class AccountDeleteConfirm:
    """Class for confirming account deletion."""
    def confirm(self):
        """Confirm account deletion"""
        raise NotImplementedError('Deletion system not implemented!')


class Account:
    """All-in-one class for managing accounts."""
    def __init__(self, discord_id: int) -> None:
        """
        Initialize the class.

        :param discord_id: The Discord user ID associated with the account.
        """
        self.discord_id = discord_id

        self.refresh()


    def __repr__(self):
        return (
            f'{self.__class__.__name__}('
            f'discord_id={self.discord_id}, '
            f'account_id={self.account_id}, '
            f'creation_date="{self.creation_date}", '
            f'blacklisted={self.blacklisted})'
        )


    def refresh(self):
        """Refresh the class data."""
        # distiguishable default object
        self.__default = object()

        self._linking_manager = self.__default
        self._historical_manager = self.__default
        self._permission_manager = self.__default
        self._subscription_manager = self.__default
        self._theme_manager = self.__default

        self._player_name = self.__default
        self._player_uuid = self.__default
        self._subscription = self.__default

        self._account_id = self.__default
        self._creation_timestamp = self.__default
        self._creation_date = self.__default
        self._permissions = self.__default
        self._blacklisted = self.__default
        self._exists = self.__default

        self._owned_themes = self.__default
        self._available_themes = self.__default
        self._active_theme = self.__default

        self._votes = self.__default
        self._weekend_votes = self.__default
        self._last_vote_timestamp = self.__default
        self._last_vote_date = self.__default

        self._commands_ran = self.__default


    def _load_account_table(self):
        """Attempt to load account data from the database."""
        # Loading has already been attempted and account didn't exist.
        if self._exists is False:
            return

        account = get_account(self.discord_id)

        if account:
            self._exists = True

            self._account_id = account.account_id
            self._creation_timestamp = account.creation_timestamp
            self._permissions = comma_separated_to_list(account.permissions)
            self._blacklisted = bool(account.blacklisted)

            return

        self._exists = False


    def _load_voting_data(self):
        """Load voting related data from the database."""
        voting_data = get_voting_data(self.discord_id)

        if voting_data:
            self._votes = voting_data[1]
            self._weekend_votes = voting_data[2]
            self._last_vote_timestamp = voting_data[3]
        else:
            self._votes = 0
            self._weekend_votes = 0
            self._last_vote_timestamp = None


    def create(self,
        account_id: int=None,
        creation_timestamp: float=None,
        permissions: list | str=None,
        blacklisted: bool=False
    ) -> None:
        """
        Create a new user account if one doesn't already exist.

        :param account_id: Overrides the default autoincrement account ID.
        :param creation_timestamp: Overrides the default creation timestamp \
            of the account.
        :param permissions: Set the user's initial permissions.
        :param blacklisted: Set whether the account is initially blacklisted.
        """
        create_account(
            discord_id=self.discord_id,
            account_id=account_id,
            creation_timestamp=creation_timestamp,
            permissions=permissions,
            blacklisted=blacklisted
        )
        self._exists = True


    def delete(self) -> AccountDeleteConfirm:
        """Delete the account. (NOT IMPLEMENTED)"""
        return AccountDeleteConfirm()


    def set_blacklisted(self, blacklisted: bool=True):
        """Blacklist or unblacklist the account."""
        set_account_blacklist(self.discord_id, blacklisted)


    def has_access(
        self,
        permissions: str | list,
        allow_star: bool=True
    ) -> bool:
        """
        Check if a user's account has access to one or more of the
        specified permission(s), accounting for permissions derived
        from subscriptions.

        :param permissions: The permission(s) to check that the user has one more of.
        :param allow_star: Allow star (*) permission to overrule permission checks.
        :return bool: Whether the user has derived access to the specified permissions.
        """
        return has_access(self.discord_id, permissions, allow_star)


    def has_permission(
        self,
        permissions: str | list,
        allow_star: bool=True
    ) -> bool:
        """
        Check if the user's account explicitly has one more of the specified
        permissions.

        :param permissions: The permission(s) to check for.
        :param allow_star: Allow star (*) permission to overrule permission checks.
        :return bool: Whether the user has the specified permission(s).
        """
        return has_permission(self.discord_id, permissions, allow_star)


    @property
    def account_id(self) -> float:
        """The account's locally assigned ID (not Discord ID)."""
        if self._account_id is self.__default:
            self._load_account_table()
        return self._account_id

    @property
    def creation_timestamp(self) -> float:
        """The account's creation timestamp (UTC time)."""
        if self._creation_timestamp is self.__default:
            self._load_account_table()
        return self._creation_timestamp

    @property
    def creation_date(self) -> str | None:
        """The creating date of the user account (formatted as `%d/%m/%Y`, UTC time)"""
        if self._creation_date is self.__default:
            if self.creation_timestamp is not self.__default:
                creation = datetime.fromtimestamp(self.creation_timestamp, UTC)
                self._creation_date = creation.strftime('%d/%m/%Y')
            else:
                self._creation_date = None
        return self._creation_date

    @property
    def permissions(self) -> list:
        """A list of custom permissions that the user has."""
        if self._permissions is self.__default:
            self._load_account_table()
        return self._permissions

    @property
    def blacklisted(self) -> bool:
        """Whether the user is blacklisted."""
        if self._blacklisted is self.__default:
            self._load_account_table()
        return self._blacklisted

    @property
    def exists(self) -> bool:
        """Whether the account exists."""
        if self._exists is self.__default:
            self._load_account_table()
        return self._exists

    @property
    def player_name(self) -> str | None:
        """The username corresponding to the linked player UUID."""
        if self._player_name is self.__default:
            if self.player_uuid is not None:
                self._player_name = FetchPlayer2(self.player_uuid).name
            else:
                self._player_name = None
        return self._player_name

    @property
    def player_uuid(self) -> str | None:
        """The UUID of the linked player."""
        if self._player_uuid is self.__default:
            self._player_uuid = get_linked_player(self.discord_id)
        return self._player_uuid

    @property
    def subscription(self) ->  Subscription:
        """The subscription tier of the user account."""
        if self._subscription is self.__default:
            self._subscription = self.subscription_manager.get_subscription()
        return self._subscription

    @property
    def owned_themes(self) -> list:
        """A list of owned themes that the user account has."""
        if self._owned_themes is self.__default:
            self._owned_themes = get_owned_themes(self.discord_id)
        return self._owned_themes

    @property
    def available_themes(self) -> list:
        """A list of available themes that the user can select."""
        if self._available_themes is self.__default:
            self._available_themes = get_voter_themes() + self.owned_themes
        return self._available_themes

    @property
    def active_theme(self) -> str:
        """The active theme that the user has selected for use."""
        if self._active_theme is self.__default:
            self._active_theme = get_active_theme(self.discord_id)
        return self._active_theme

    @property
    def votes(self) -> int:
        """The total number of times the user has voted for the bot."""
        if self._votes is self.__default:
            self._load_voting_data()
        return self._votes

    @property
    def weekend_votes(self) -> int:
        """
        The total number of times the user has upvoted the bot during the weekend.
        Only counts weekend votes for participating bot listing sites.
        """
        if self._weekend_votes is self.__default:
            self._load_voting_data()
        return self._weekend_votes

    @property
    def last_vote_timestamp(self) -> float | None:
        """The timestamp of the last time the user upvoted the bot."""
        if self._last_vote_timestamp is self.__default:
            self._load_voting_data()
        return self._last_vote_timestamp

    @property
    def last_vote_date(self) -> float | None:
        """The date when the user last voted (formatted as `%d/%m/%Y`, UTC time)."""
        if self._last_vote_date is self.__default:
            if self.last_vote_timestamp:
                last_vote = datetime.fromtimestamp(self.last_vote_timestamp, UTC)
                self._last_vote_date = last_vote.strftime('%d/%m/%Y')
            else:
                self._last_vote_date = None
        return self._last_vote_date

    @property
    def commands_ran(self):
        if self._commands_ran is self.__default:
            self._commands_ran = commands_ran(self.discord_id)
        return self._commands_ran


    @property
    def linking_manager(self) -> LinkingManager:
        """A linking manager for the account."""
        if self._linking_manager is self.__default:
            self._linking_manager = LinkingManager(self.discord_id)
        return self._linking_manager

    @property
    def permission_manager(self) -> PermissionManager:
        """A permissions manager for the account."""
        if self._permission_manager is self.__default:
            self._permission_manager = PermissionManager(self.discord_id)
        return self._permission_manager

    @property
    def subscription_manager(self) -> SubscriptionManager:
        """A subscription manager for the account."""
        if self._subscription_manager is self.__default:
            self._subscription_manager = SubscriptionManager(self.discord_id)
        return self._subscription_manager

    @property
    def theme_manager(self) -> ThemeManager:
        """A themes manager for the account."""
        if self._theme_manager is self.__default:
            self._theme_manager = ThemeManager(self.discord_id)
        return self._theme_manager
