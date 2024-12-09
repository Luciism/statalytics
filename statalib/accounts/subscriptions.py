"""Account subscriptions related functionality."""

import json
import socket
from dataclasses import dataclass
from datetime import datetime, UTC
from typing import Any

from ..db import ensure_cursor, Cursor
from ..cfg import config


class UnregisteredPackageError(Exception):
    """Error class for if a package does not exist in the config file."""

class PackageTierConflictError(Exception):
    """Error class for if there's a conflict between two different package tiers."""


@dataclass
class Subscription:
    """Subscription data class"""
    package: str
    "The subscription package"
    expiry_timestamp: float | int | None
    """The expiry timestamp of the subscription,
    or `None` if the subscription is permanent"""


    def expires_in(self) -> float | None:
        """
        The subscription duration remaining in seconds.

        :return: The duration remaining, otherwise `None` if the subscription is permanent.
        """
        if self.expiry_timestamp is None:
            return None
        return self.expiry_timestamp - datetime.now(UTC).timestamp()


    @staticmethod
    def get_package_tier(package: str) -> int:
        """
        Static method that returns the numeric tier of a certain package.

        *If using an instantiated instance of `Subscription`, use the `.tier`
        property instead.*

        :param package: The package to return the tier of.
        :raises statalib.subscriptions.UnregisteredPackageError: The package \
            is not registered in the config file.
        """
        try:
            return config(f"global.subscriptions.packages.{package}.tier")
        except KeyError as exc:
            raise UnregisteredPackageError(
                "The package entered was not found in the config file!"
            ) from exc


    @property
    def tier(self) -> int:
        """The numeric tier of the subscription package."""
        return self.get_package_tier(self.package)


    @staticmethod
    def __get_package_data(package: str) -> None:
        packages_config: dict[str, dict] = config('global.subscriptions.packages')
        package_data = packages_config.get(package)

        if package_data is None:
            raise UnregisteredPackageError(
                "The package entered was not found in the config file!")
        return package_data

    @staticmethod
    def get_package_permissions(package: str) -> list[str]:
        """
        Static method that returns a list of the configured permissions
        for a given package.

        *If using an instantiated instance of `Subscription`,
        use the `.package_permissions` property instead.*

        :param package: The package to get the permissions for.
        :return: A list of the package's configured permissions.
        :raises statalib.subscriptions.UnregisteredPackageError: The package \
            is not registered in the config file.
        """
        package_data = Subscription.__get_package_data(package)
        package_perms = package_data.get('permissions', [])
        return package_perms


    @property
    def package_permissions(self) -> list[str]:
        """The permissions that the package tier includes."""
        return self.get_package_permissions(self.package)


    @staticmethod
    def get_package_property(
        package: str,
        property: str,
        default: Any=None
    ) -> list[str]:
        """
        Static method that returns a property value configured
        for the respective package.

        *If using an instantiated instance of `Subscription`,
        use the `.package_property()` method instead.*

        :param package: The package to get the property for.
        :param property: The property name to get the value for.
        :param default: The default value to return if no value is found.
        :return: The property value, or the default value if no value is found.
        """
        package_data = Subscription.__get_package_data(package)
        properties: dict = package_data.get('properties', {})
        return properties.get(property, default)


    def package_property(self, property: str, default: Any=None) -> list[str]:
        """
        Returns the configured property value for the given property.

        :param property: The property name to get the value for.
        :param default: The default value to return if no value is found.
        :return: The property value, or the default value if no value is found.
        """
        return self.get_package_property(self.package, property, default)


class AccountSubscriptions:
    """Class to manage user subscriptions."""
    def __init__(self, discord_id: int) -> None:
        """
        Class to manage user subscriptions.

        :param discord_id: The Discord user ID of the respective user.
        """
        self._discord_id = discord_id


    def __update_user_roles(self, subscription: Subscription) -> None:
        if not config.SHOULD_UPDATE_SUBSCRIPTION_ROLES:  # Overrules everything
            return

        json_data = json.dumps({
            "action": "dispatch_event",
            "event_name": "subscription_update",
            "args": [
                self._discord_id,
                subscription.package,
                subscription.expiry_timestamp
            ]
        })

        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
                client.connect(('utils', config("apps.utils.socket_server_port")))
                client.send(json_data.encode())
        except (ConnectionRefusedError, socket.gaierror):
            return  # Utils bot is probably offline


    def __set_active_subscription(
        self,
        subscription: Subscription,
        cursor: Cursor
    ) -> None:
        cursor.execute(
            "SELECT * FROM subscriptions_active WHERE discord_id = ?", (self._discord_id,))

        if cursor.fetchone():
            query = ("UPDATE subscriptions_active SET package = ?, "
                "expires = ? WHERE discord_id = ?")
        else:
            query = ("INSERT INTO subscriptions_active "
                "(package, expires, discord_id) VALUES (?, ?, ?)")

        # Set active subscription to provided subscription
        cursor.execute(
            query,
            (subscription.package, subscription.expiry_timestamp, self._discord_id)
        )


    def __update_active_subscription(
        self,
        cursor: Cursor
    ) -> Subscription:
        """
        Update the active subscription based on the paused subscriptions.
        :param cursor: A database cursor to operate on.
        :return: The updated active subscription of the user.
        """
        # Select all paused package data
        cursor.execute(
            "SELECT package, duration_remaining, id FROM subscriptions_paused "
            "WHERE discord_id = ?", (self._discord_id,)
        )
        paused_subscriptions = cursor.fetchall()

        # User has no paused subscriptions
        if not paused_subscriptions:
            # Return the default subscription as well as a filler callable
            # because no further action is required.
            return Subscription(config("global.subscriptions.default_package"), None)

        # Get package with highest tier property
        highest_tier_package = paused_subscriptions[0]

        for sub in paused_subscriptions[1:]:
            if (
                config(f"global.subscriptions.packages.{sub[0]}.tier")
                > config(f"global.subscriptions.packages.{highest_tier_package[0]}.tier")
            ):
                highest_tier_package = sub

        # Create subscription object from highest tier paused package
        if highest_tier_package[1] is not None:  # Package duration is not permanent
            expiry_timestamp = datetime.now(UTC).timestamp() + highest_tier_package[1]
        else:
            expiry_timestamp = None

        subscription = Subscription(
            package=highest_tier_package[0], expiry_timestamp=expiry_timestamp
        )

        # Insert or update new active subscription data
        self.__set_active_subscription(subscription, cursor)

        # Remove paused subscription
        cursor.execute(
            "DELETE FROM subscriptions_paused WHERE discord_id = ? AND id = ?",
            (self._discord_id, highest_tier_package[2])
        )

        return subscription


    @ensure_cursor
    def get_subscription(
        self,
        update_roles: bool=True,
        *, cursor: Cursor=None
    ) -> Subscription:
        """
        Get the user's current subscription.

        :param update_roles: Whether or not to update the user's subscription \
            Discord roles if their subscription state is updated.
        :param cursor: A custom `Cursor` object to operate on.
        :return Subscription: The user's current subscription.
        """
        cursor.execute(
            "SELECT package, expires FROM subscriptions_active WHERE discord_id = ?",
            (self._discord_id,))

        active_subscription = cursor.fetchone()

        if active_subscription is None:
            return Subscription(config("global.subscriptions.default_package"), None)

        # Check if subscription has expired (and isn't lifetime)
        if active_subscription[1] and \
            active_subscription[1] < datetime.now(UTC).timestamp():
            # Update subscription data
            subscription = self.__update_active_subscription(cursor)
        else:
            subscription = Subscription(
                package=active_subscription[0],
                expiry_timestamp=active_subscription[1]
            )

        # Update user roles
        if update_roles:
            self.__update_user_roles(subscription)
        return subscription


    @ensure_cursor
    def _get_paused_subscriptions(
        self,
        package: str | None=None,
        *, cursor: Cursor=None
    ) -> list[tuple]:
        query = ("SELECT package, duration_remaining "
            "FROM subscriptions_paused WHERE discord_id = ?")

        if package is None:
            cursor.execute(query, (self._discord_id,))
            return cursor.fetchall()

        query += " AND package = ?"
        cursor.execute(query, (self._discord_id, package))
        return cursor.fetchall()


    @ensure_cursor
    def _add_paused_subscription(
        self,
        package: str,
        duration_remaining: float | None,
        *, cursor: Cursor=None
    ) -> None:
        cursor.execute(
            "INSERT INTO subscriptions_paused (discord_id, package, duration_remaining) "
            "VALUES (?, ?, ?)", (self._discord_id, package, duration_remaining)
        )


    @ensure_cursor
    def has_package_conflicts(
        self,
        package: str,
        *, cursor: Cursor=None
    ) -> bool:
        """
        Check whether a certain adding a certain package to a user's
        subscription will have conflicts with their existing subscription.

        :param package: The package to check for conflicts against.
        :return bool: Whether (or not) there are conflicts.
        """
        package_tier = Subscription.get_package_tier(package)
        subscription = self.get_subscription(cursor=cursor)

        # Active subscription package is permanent
        if subscription.expiry_timestamp is None:
            # Package tier is not a higher tier than active subscription package
            if package_tier <= subscription.tier:
                return True
        return False


    def __add_subscription_existing_subscription(
        self,
        cursor: Cursor,
        existing_subscription: Subscription,
        package: str,
        duration: float
    ) -> None:
        # New subscription is same tier as existing one
        if package == existing_subscription.package:
            # Check if existing subscription is a lifetime subscription
            if existing_subscription.expiry_timestamp is None:
                raise PackageTierConflictError(
                    "The package you are trying to add is the same tier as the currently "
                    "active subscription package. Because the currently active subscription "
                    "package has an infinite duration, it cannot be extended."
                )

            if duration is None:
                # Subscription being added is a lifetime subscription
                expires = None

                # Pause active subscription (preserve it)
                self._add_paused_subscription(
                    existing_subscription.package,
                    existing_subscription.expires_in(),
                    cursor=cursor)
            else:
                if existing_subscription.expires_in() > 0:
                    # Extend existing subscription because it is still running
                    expires = existing_subscription.expiry_timestamp + duration
                else:
                    # Set expiry to now + duration because existing subscription has expired
                    expires = datetime.now(UTC).timestamp() + duration

            cursor.execute(
                "UPDATE subscriptions_active SET expires = ? WHERE discord_id = ?",
                (expires, self._discord_id)
            )
            return

        # New subscription is higher tier than existing one
        if Subscription.get_package_tier(package) > existing_subscription.tier:
            # Pause active subscription and activate new subscription
            self._add_paused_subscription(
                existing_subscription.package, existing_subscription.expires_in(), cursor=cursor)

            new_subscription = Subscription(
                package, datetime.now(UTC).timestamp() + duration)
            self.__set_active_subscription(new_subscription, cursor)
            return

        # New subscription is lower tier than existing one
        # Check if existing package is a lifetime subscription
        if existing_subscription.expiry_timestamp is None:
            raise PackageTierConflictError(
                "The package you are attempting to add is a lower tier than "
                "the currently active subscription package. Because the currently "
                "active subscription package has an infinite duration, the "
                "package you are attempting to add can never be activated."
            )

        self._add_paused_subscription(package, duration, cursor=cursor)


    @ensure_cursor
    def add_subscription(
        self,
        package: str,
        duration: float | None=None,
        update_roles: bool=True,
        *, cursor: Cursor=None
    ) -> None:
        """
        Adds a subscription to the user's account.

        :param package: The subscription package to add.
        :param duration: The duration (in seconds) of the subscription. Can be \
            left as `None` for an infinite duration.
        :param update_roles: Whether or not to update the user's subscription \
            Discord roles if their subscription state is updated.
        """
        # Ensure active subscription is accurate
        active_subscription = self.get_subscription(
            update_roles=False, cursor=cursor)

        # User has no active subscription.
        # Simply add the subscription to the user's account
        if (
            active_subscription.package == config("global.subscriptions.default_package")
        ):
            # There may be an expired subscription in the active subscriptions table
            cursor.execute(
                "DELETE FROM subscriptions_active WHERE discord_id = ?",
                (self._discord_id,))

            # Insert new subscription
            if duration is not None:
                expires = datetime.now(UTC).timestamp() + duration
            else:
                expires = None

            cursor.execute(
                "INSERT INTO subscriptions_active (discord_id, package, expires) "
                "VALUES (?, ?, ?)", (self._discord_id, package, expires)
            )

            new_subscription = Subscription(package, expires)

        else:
            self.__add_subscription_existing_subscription(
                cursor, active_subscription, package, duration
            )

        if update_roles:
            new_subscription = self.get_subscription(
                update_roles=False, cursor=cursor)

            self.__update_user_roles(new_subscription)
