"""Account permissions related functionality."""

from ._create import create_account
from ..functions import comma_separated_to_list, db_connect
from .subscriptions import AccountSubscriptions


class AccountPermissions:
    """Manager for account permissions."""
    def __init__(self, discord_user_id: int) -> None:
        self._discord_user_id = discord_user_id

    def add_permission(self, permission: str) -> None:
        """
        Add a permission to a user if they don't already have it.

        :param permission: The permission to add to the user.
        """
        permissions = self.get_permissions()

        if permission not in permissions:
            permissions.append(permission)
            self.set_permissions(permissions)

    def remove_permission(self, permission: str) -> None:
        """
        Remove a permission from a user.

        :param permission: The permission to remove from the user.
        """
        permissions = self.get_permissions()

        if permission in permissions:
            while permission in permissions:
                permissions.remove(permission)
            self.set_permissions(permissions)

    def set_permissions(self, permissions: list) -> None:
        """
        Set the user's permissions to the given set of permissions.
        This will completely override any existing permissions.

        :param permissions: A list of permissions to set for the user.
        """
        permissions = list(set(permissions))  # Remove duplicates.
        permissions_str = ','.join(permissions)

        with db_connect() as conn:
            cursor = conn.cursor()

            cursor.execute(
                'SELECT account_id FROM accounts WHERE discord_id = ?',
                (self._discord_user_id,))
            existing_data: tuple = cursor.fetchone()

            if existing_data:
                cursor.execute(
                    "UPDATE accounts SET permissions = ? WHERE discord_id = ?",
                    (permissions_str, self._discord_user_id))
            else:
                create_account(self._discord_user_id, permissions=permissions)

    def get_permissions(self) -> list[str]:
        """
        Get a list of the user's permissions.

        :return list: A list of the user's permissions.
        """
        with db_connect() as conn:
            cursor = conn.cursor()

            create_account(self._discord_user_id)

            cursor.execute(
                'SELECT permissions FROM accounts WHERE discord_id = ?',
                (self._discord_user_id,))
            permissions: tuple = cursor.fetchone()

        if permissions:
            return comma_separated_to_list(permissions[0])
        return []

    def has_permission(
        self, permissions: str | list[str], allow_star: bool=True
    ) -> bool:
        """
        Check if a user has one or more of the specified permissions.

        :param permissions: The permission(s) to check that the user has one more of.
        :param allow_star: Allow star (*) permission to overrule permission checks.
        :return bool: Whether the user has derived access to the specified permissions.
        """
        user_permissions = self.get_permissions()

        if allow_star and '*' in user_permissions:
            return True

        if isinstance(permissions, str):
            permissions = [permissions]

        # at least one permission is in user_permissions
        if set(permissions) & set(user_permissions):
            return True

        return False

    def has_access(
        self, permissions: str | list[str], allow_star: bool=True
    ) -> bool:
        """
        Check if a user's account has access to one or more of the
        specified permission(s), accounting for permissions derived
        from subscriptions.

        :param permissions: The permission(s) to check that the user has one more of.
        :param allow_star: Allow star (*) permission to overrule permission checks.
        :return bool: Whether the user has derived access to the specified permissions.
        """
        if not self._discord_user_id:
            return False

        subscription = AccountSubscriptions(self._discord_user_id).get_subscription()
        package_perms = subscription.package_permissions

        package_perms = set(package_perms)

        user_permissions = self.get_permissions()

        for user_permission in user_permissions:
            package_perms.add(user_permission)

        if '*' in package_perms and allow_star:
            return True

        if isinstance(permissions, str):
            permissions = [permissions]

        # User has at least one of the following permissions.
        if set(permissions) & package_perms:
            return True

        return False
