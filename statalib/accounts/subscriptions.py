"""Account subscriptions related functionality."""

import asyncio
from dataclasses import dataclass
from datetime import datetime, UTC
import threading
from typing import Any

from ..redis_ext import SubscriptionUpdate, RedisStreamProducer
from ..redis_ext.client import RedisClient, redis_client as main_redis_client

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
    id: int | None=None
    """The ID of the subscription if it is paused."""

    def as_dict(self) -> dict:
        return {
            "package": self.package,
            "expiry_timestamp": self.expiry_timestamp,
            "duration_remaining": self.expires_in(),
            "id": self.id
        }

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

    @property
    def is_default(self) -> bool:
        """Whether the subscription is the default (free) subscription."""
        return self == self.default()

    @staticmethod
    def default() -> 'Subscription':
        """Get the default (free) subscription info."""
        return Subscription(config("global.subscriptions.default_package"), None)

    @staticmethod
    def create_timestamp(add: float | int) -> float:
        """Add a value to the current UTC timestamp."""
        return datetime.now(UTC).timestamp() + add

class _SubUtils:
    @staticmethod
    def subscription_obj_from_row(row: tuple) -> Subscription:
        """Build a `~Subscription` object from a database row."""
        if row:
            return Subscription(*row)
        return None

    @staticmethod
    def weight_subscription(subscription: Subscription) -> int:
        """Weight a subscription based on its tier and duration."""
        weight = subscription.tier

        # Subscription is a lifetime subscription
        if subscription.expiry_timestamp is None:
            # Bump the subscription above subscriptions of the same tier but not higher tiers.
            weight += 0.5

        return weight

    @staticmethod
    def extract_active_subscription_from_all_subscriptions(
        all_subscriptions: list[Subscription]
    ) -> tuple[Subscription, list[Subscription]]:
        """
        Creates the best possible active subscription from a list of subscriptions.

        :param all_subscriptions: A list of subscriptions.
        :return tuple: A tuple of the best possible active subscription and the \
            remaining subscriptions.
        """
        if not all_subscriptions:
            return None, []

        # Weight all the subscriptions
        weighted_subscriptions = [
            (_SubUtils.weight_subscription(sub), sub)
            for sub in all_subscriptions
        ]

        # Find the greatest weight and the subscriptions with the same greatest weight
        greatest_weight = max([w[0] for w in weighted_subscriptions])
        subscriptions_with_greatest_weight = [
            w[1] for w in weighted_subscriptions if w[0] == greatest_weight
        ]

        # Combine subscriptions with the same greatest weight into one
        if len(subscriptions_with_greatest_weight) > 1:
            # Combine all durations together
            subscription_duration = sum([
                sub.expires_in() for sub in subscriptions_with_greatest_weight])

            # Create a new subscription with the combined duration
            new_active_subscription = Subscription(
                subscriptions_with_greatest_weight[0].package,
                datetime.now(UTC).timestamp() + subscription_duration
            )
        else:
            # Probably has an infinite duration
            new_active_subscription = subscriptions_with_greatest_weight[0]

        # Make the paused subscriptions list exclude the subscriptions that were made active.
        paused_subscriptions = [
            subscription for subscription in all_subscriptions
            if subscription not in subscriptions_with_greatest_weight
        ]

        return new_active_subscription, paused_subscriptions


class AccountSubscriptions:
    """Class to manage user subscriptions."""
    def __init__(self, discord_id: int, redis_client: RedisClient | None = None) -> None:
        """
        Class to manage user subscriptions.

        :param discord_id: The Discord user ID of the respective user.
        """
        self._discord_id: int = discord_id
        self._redis_client: RedisClient = redis_client or main_redis_client


    async def __async_update_user_roles(self) -> None:
        if not config.SHOULD_UPDATE_SUBSCRIPTION_ROLES:  # Overrules everything
            return

        await RedisStreamProducer(self._redis_client.client).add_subscription_update(
            SubscriptionUpdate(self._discord_id)
        )

    def __update_user_roles(self) -> None:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            threading.Thread(target=loop.run_forever, daemon=True).start()

        _ = asyncio.run_coroutine_threadsafe(self.__async_update_user_roles(), loop)
        # try:
        #     loop = asyncio.get_running_loop()
        #     _ = loop.create_task(self.__async_update_user_roles())
        # except RuntimeError:
        #     # asyncio.run(self.__async_update_user_roles())
        #     loop = asyncio.new_event_loop()
        #     loop.run(self.__async_update_user_roles())


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
            return Subscription.default()

        active_subscription = Subscription(*active_subscription)

        # Check if subscription has expired (and isn't lifetime)
        if (
            active_subscription.expiry_timestamp and
            active_subscription.expiry_timestamp < datetime.now(UTC).timestamp()
        ):
            # Update subscription data
            active_subscription, paused_subscriptions = self.determine_user_subscription_updates()
            self.set_subscriptions(active_subscription, paused_subscriptions)

            if active_subscription is None:
                return Subscription.default()

        # Update user roles
        if update_roles:
            self.__update_user_roles()
        return active_subscription


    @ensure_cursor
    def has_package_conflicts(
        self,
        new_subscription: Subscription,
        *, cursor: Cursor=None
    ) -> bool:
        """
        Check whether a certain adding a certain subscription to a user's
        subscriptions will have conflicts with their existing subscription.

        :param new_subscription: The subscription to check for conflicts against.
        :return bool: Whether (or not) there are conflicts.
        """
        try:
            self.determine_user_subscription_updates(
                added_subscription=new_subscription, cursor=cursor)
            return False
        except PackageTierConflictError:
            return True

    @staticmethod
    def determine_subscription_updates(
        all_subscriptions: list[Subscription],
        added_subscription: Subscription | None=None,
    ) -> tuple[Subscription | None, list[Subscription]]:
        # Ensure added subscription doesn't conflict with existing subscriptions
        existing_lifetime_subscriptions = [
            sub for sub in all_subscriptions if sub.expiry_timestamp is None
        ]

        if added_subscription is not None:
            # Raise error if there is an existing lifetime package with the same or higher tier.
            # Adding another package would be entirely pointless in this case.
            for subscription in existing_lifetime_subscriptions:
                if subscription.tier >= added_subscription.tier:
                    raise PackageTierConflictError(
                        "There is an existing lifetime subscription "
                        "that conflicts with the added subscription.")

            # Include the added subscription
            all_subscriptions.append(added_subscription)

        active_subscription, paused_subscriptions = _SubUtils \
            .extract_active_subscription_from_all_subscriptions(all_subscriptions)

        return active_subscription, paused_subscriptions

    @ensure_cursor
    def determine_user_subscription_updates(
        self,
        added_subscription: Subscription | None=None,
        *, cursor: Cursor=None
    ) -> tuple[Subscription | None, list[Subscription]]:
        """
        Determines what active and paused subscriptions the user should have.

        **NOTE:** This method wraps the `determine_subscription_updates` method but extends it
        to automatically use the user's current subscription data.

        :param added_subscription: Optionally add another subscription to be factored in.
        :param all_subscriptions: Optionally add multiple subscriptions to be factored \
            in, may include an active subscription and multiple paused subscriptions.
        :return tuple: A tuple of the new active and paused subscriptions.
        :raise PackageTierConflictError: If there is a conflict between the added \
            subscription and existing subscriptions.
        """
        # Select all existing subscription data.
        active_subscription_row = cursor.execute(
            "SELECT package, expires FROM subscriptions_active WHERE discord_id = ?",
            (self._discord_id,)).fetchone()
        active_subscription = _SubUtils.subscription_obj_from_row(active_subscription_row)

        paused_subscription_rows = cursor.execute(
            "SELECT package, duration_remaining, id FROM subscriptions_paused "
            "WHERE discord_id = ?", (self._discord_id,)).fetchall()
        all_subscriptions = [
            _SubUtils.subscription_obj_from_row((
                row[0],
                (datetime.now(UTC).timestamp() + row[1]
                    if row[1] is not None
                    else row[1]),  # FIXME: duration will drain as code runs
                row[2],
            ))
            for row in paused_subscription_rows
        ]

        # Include the active subscription if it hasn't expired
        if active_subscription is not None:
            expires_in = active_subscription.expires_in()
            if not expires_in or expires_in > 0:
                all_subscriptions.append(active_subscription)

        return self.determine_subscription_updates(
            all_subscriptions, added_subscription=added_subscription)



    @ensure_cursor
    def set_subscriptions(
        self,
        active_subscription: Subscription | None,
        paused_subscriptions: list[Subscription],
        *, cursor: Cursor=None
    ) -> None:
        """
        Set the user's active and paused subscriptions directly.

        **WARNING:** This method will remove any existing subscription data,
        use this only if you know what you're doing.

        :param active_subscription: The active subscription to set for the user.
        :param paused_subscriptions: The paused subscriptions to set for the user.
        """
        # Remove old subscription data
        cursor.execute(
            "DELETE FROM subscriptions_active WHERE discord_id = ?", (self._discord_id,))
        cursor.execute(
            "DELETE FROM subscriptions_paused WHERE discord_id = ?", (self._discord_id,))

        # Add new subscription data
        if active_subscription is not None:
            cursor.execute(
                "INSERT INTO subscriptions_active (discord_id, package, expires) "
                "VALUES (?, ?, ?)", (self._discord_id, active_subscription.package,
                active_subscription.expiry_timestamp))

        for paused_sub in paused_subscriptions:
            cursor.execute(
                "INSERT INTO subscriptions_paused (discord_id, package, duration_remaining) "
                "VALUES (?, ?, ?)", (self._discord_id, paused_sub.package,
                paused_sub.expires_in())
            )


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
        :raise PackageTierConflictError: If there is an existing lifetime \
            subscription with the same or higher tier.
        """
        if duration is not None:
            expiry_timestamp = datetime.now(UTC).timestamp() + duration
        else:
            expiry_timestamp = None

        # Determine new subscription data
        active_subscription, paused_subscriptions = self.determine_user_subscription_updates(
            Subscription(package, expiry_timestamp), cursor=cursor
        )

        self.set_subscriptions(
            active_subscription, paused_subscriptions, cursor=cursor)

        if update_roles:
            self.__update_user_roles()


    @ensure_cursor
    def remove_active_subscription(
        self,
        update_roles: bool=True,
        *, cursor: Cursor=None
    ) -> None:
        """
        Delete the user's current active subscription. This will activate
        any paused subscription that should take its place.

        :param update_roles: Whether or not to update the user's subscription \
            Discord roles if their subscription state is updated.
        """
        cursor.execute(
            "DELETE FROM subscriptions_active WHERE discord_id = ?", (self._discord_id,))

        active_subscription, paused_subscriptions = self\
            .determine_user_subscription_updates(cursor=cursor)
        self.set_subscriptions(
            active_subscription, paused_subscriptions, cursor=cursor)

        if update_roles:
            self.__update_user_roles()


    @ensure_cursor
    def remove_paused_subscription(
        self,
        paused_subscription_id: int,
        *, cursor: Cursor=None
    ) -> None:
        """
        Remove a paused subscription with a specified ID.

        :param paused_subscription_id: The ID of the paused subscription to remove.
        """
        cursor.execute(
            "DELETE FROM subscriptions_paused WHERE discord_id = ? AND id = ?",
            (self._discord_id, paused_subscription_id))
        # No need to update user roles or subscriptions

    @ensure_cursor
    def get_paused_subscriptions(
        self,
        package: str | None=None,
        *, cursor: Cursor=None
    ) -> list[Subscription]:
        query = (
            "SELECT package, duration_remaining, id "
            "FROM subscriptions_paused WHERE discord_id = ?")
        params = [self._discord_id]

        if package is not None:
            params.append(package)
            query += " AND package = ?"

        cursor.execute(query, params)
        results = cursor.fetchall()

        return [Subscription(
            result[0],
            (datetime.now(UTC).timestamp() + result[1]
                if result[1] is not None
                else result[1]),  # FIXME
            result[2]
        ) for result in results]


    @ensure_cursor
    def delete_all_subscription_data(
        self,
        update_roles: bool=True,
        *, cursor: Cursor=None
    ) -> None:
        """
        Delete any subscription data associated with the user. This includes both
        active and paused subscriptions.

        :param update_roles: Whether or not to update the user's subscription \
            Discord roles if their subscription state is updated.
        """
        cursor.execute(
            "DELETE FROM subscriptions_active WHERE discord_id = ?", (self._discord_id,))
        cursor.execute(
            "DELETE FROM subscriptions_paused WHERE discord_id = ?", (self._discord_id,))

        if update_roles:
            self.__update_user_roles()

