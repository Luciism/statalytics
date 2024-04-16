import sqlite3
from dataclasses import dataclass
from datetime import datetime, UTC
from typing import Callable

from .cfg import config


class UnregisteredPackageError(Exception):
    """Error class for if a package does not exist in the config file."""

class PackageTierConflictError(Exception):
    """Error class for if there's a conflict between two different package tiers."""


@dataclass
class Subscription:
    """Subscription data class"""
    package: str
    expiry_timestamp: float | int | None

    def expires_in(self) -> float | None:
        """
        The duration remaining of the subscription in seconds.
        :return: remaining time, otherwise `None` if the subscription is permanent
        """
        if self.expiry_timestamp is None:
            return None
        return self.expiry_timestamp - datetime.now(UTC).timestamp()

    @staticmethod
    def get_package_tier(package: str) -> int:
        """
        Abstract method that returns the numeric tier of a certain package.
        If using an instantiated instance of `Subscription`, use the `.tier`
        property instead.
        :param package: The package to return the tier of.
        :raises: `statalib.subscriptions.UnregisteredPackageError` - The package \
            is not registered in the config file.
        """
        try:
            return config(f"packages.{package}.tier")
        except KeyError as exc:
            raise UnregisteredPackageError(
                "The package entered was not found in the config file!"
            ) from exc

    @property
    def tier(self) -> int:
        """The numeric tier of the subscription package."""
        return self.get_package_tier(self.package)


class SubscriptionManager:
    """Class to manage user subscriptions."""
    def __init__(self, discord_id: int) -> None:
        """
        Class to manage user subscriptions.
        :param discord_id: the discord id of the respective user
        """
        self._discord_id = discord_id

    def __set_active_subscription(
        self,
        subscription: Subscription,
        cursor: sqlite3.Cursor
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
        cursor: sqlite3.Cursor
    ) -> tuple[Subscription, Callable]:
        """
        Updates active subscription based on paused subscriptions.
        :param cursor: A database cursor to operate on
        :return: The new active subscription of the user as well as a callable \
            that will tell the utils bot to update the user's roles.
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
            return Subscription(config("default_package"), None), lambda: ...

        # Get package with highest tier property
        highest_tier_package = paused_subscriptions[0]

        for sub in paused_subscriptions[1:]:
            if config(f"packages.{sub[0]}.tier") \
                > config(f"packages.{highest_tier_package[0]}.tier"):
                highest_tier_package = sub

        # Create subscription object from highest tier paused package
        if highest_tier_package[1] is not None:  # Package duration is not permanent
            expiry_timestamp = int(datetime.now(UTC).timestamp() + highest_tier_package[1])
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

        def callback() -> None:
            # TODO implement callback
            ...

        return subscription, callback


    def __get_subscription(
        self,
        cursor: sqlite3.Cursor
    ) -> tuple[Subscription, Callable | None]:
        callback = None

        cursor.execute(
            "SELECT package, expires FROM subscriptions_active WHERE discord_id = ?",
            (self._discord_id,))

        active_subscription = cursor.fetchone()

        if active_subscription is None:
            return Subscription(config("default_package"), None), None

        # Check if subscription has expired (and isn't lifetime)
        if active_subscription[1] and \
            active_subscription[1] < int(datetime.now(UTC).timestamp()):
            # Update subscription data
            subscription, callback = self.__update_active_subscription(cursor)
        else:
            subscription = Subscription(
                package=active_subscription[0],
                expiry_timestamp=active_subscription[1]
            )

        return subscription, callback


    def get_subscription(
        self,
        update_roles: bool=True,
        cursor: sqlite3.Cursor=None
    ) -> Subscription:
        """
        Get the user's current subscription.
        :param update_roles: Whether or not to update the user's subscription \
            discord roles if their subscription state is updated.
        """
        if cursor is not None:
            subscription, callback = self.__get_subscription(cursor)
        else:
            with sqlite3.connect(config.DB_FILE_PATH) as conn:
                cursor = conn.cursor()
                subscription, callback = self.__get_subscription(cursor)

        # Call callback function if it exists
        if callback and update_roles:
            callback()
        return subscription


    def __get_paused_subscriptions(
        self,
        package: str | None,
        cursor: sqlite3.Cursor
    ):
        query = ("SELECT package, duration_remaining "
            "FROM subscriptions_paused WHERE discord_id = ?")

        if package is None:
            cursor.execute(query, (self._discord_id,))
            return cursor.fetchall()

        query += " AND package = ?"
        cursor.execute(query, (self._discord_id, package))
        return cursor.fetchall()

    def _get_paused_subscriptions(
        self,
        package: str | None = None,
        cursor: sqlite3.Cursor | None = None
    ) -> list[tuple]:
        if cursor is not None:
            return self.__get_paused_subscriptions(package, cursor)

        with sqlite3.connect(config.DB_FILE_PATH) as conn:
            cursor = conn.cursor()
            return self.__get_paused_subscriptions(package, cursor)


    def __add_paused_subscription(
        self,
        package: str,
        duration_remaining: int | None,
        cursor: sqlite3.Cursor
    ) -> None:
        cursor.execute(
            "INSERT INTO subscriptions_paused (discord_id, package, duration_remaining) "
            "VALUES (?, ?, ?)", (self._discord_id, package, duration_remaining)
        )

    def _add_paused_subscription(
        self,
        package: str,
        duration_remaining: int | None,
        cursor: sqlite3.Cursor | None=None
    ) -> None:
        if cursor is not None:
            return self.__add_paused_subscription(package, duration_remaining, cursor)

        with sqlite3.connect(config.DB_FILE_PATH) as conn:
            cursor = conn.cursor()
            return self.__add_paused_subscription(package, duration_remaining, cursor)



    def __add_subscription_existing_subscription(
        self,
        cursor: sqlite3.Cursor,
        existing_subscription: Subscription,
        package: str,
        duration: int
    ) -> None:
        # New subscription is same tier as existing one
        if package == existing_subscription.package:
            # Check if existing subscription is a lifetime subscription
            if existing_subscription.expiry_timestamp == None:
                raise PackageTierConflictError(
                    "The package you are trying to add is the same tier as the currently "
                    "active subscription package. Because the currently active subscription "
                    "package has an infinite duration, it cannot be extended."
                )

            if existing_subscription.expires_in() > 0:
                # Extend existing subscription because it is still running
                expires = int(existing_subscription.expiry_timestamp + duration)
            else:
                # Set expiry to now + duration because existing subscription has expired
                expires = int(datetime.now(UTC).timestamp() + duration)

            cursor.execute(
                "UPDATE subscriptions_active SET expires = ? WHERE discord_id = ?",
                (expires, self._discord_id)
            )
            return

        # New subscription is higher tier than existing one
        if Subscription.get_package_tier(package) > existing_subscription.tier:
            # Pause active subscription and activate new subscription
            self._add_paused_subscription(
                existing_subscription.package, existing_subscription.expires_in(), cursor)

            new_subscription = Subscription(
                package, int(datetime.now(UTC).timestamp() + duration))
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

        self._add_paused_subscription(package, duration, cursor)


    def add_subscription(
        self,
        package: str,
        duration: int | None=None
    ) -> bool:
        """
        Adds a subscription to the user's account.
        :param package: The subscription package to add.
        :param duration: The duration (in seconds) of the subscription. Can be \
            left as `None` for an infinite duration.
        :return: Boolean whether or not the subscription was successfully added
        """
        with sqlite3.connect(config.DB_FILE_PATH) as conn:
            cursor = conn.cursor()

            # Ensure active subscription is accurate
            active_subscription = self.get_subscription(
                update_roles=False, cursor=cursor)

            # User has no active subscription.
            # Simply add the subscription to the user's account
            if active_subscription.package == config("default_package"):
                # There may be an expired subscription in the active subscriptions table
                cursor.execute(
                    "DELETE FROM subscriptions_active WHERE discord_id = ?",
                    (self._discord_id,))

                # Insert new subscription
                if duration is not None:
                    expires = int(datetime.now(UTC).timestamp() + duration)
                else:
                    expires = None

                cursor.execute(
                    "INSERT INTO subscriptions_active (discord_id, package, expires) "
                    "VALUES (?, ?, ?)", (self._discord_id, package, expires)
                )
                return True

            self.__add_subscription_existing_subscription(
                cursor, active_subscription, package, duration
            )
