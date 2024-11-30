"""Functions for handling permissions."""

from .accounts import create_account
from .functions import comma_separated_to_list, db_connect
from .subscriptions import SubscriptionManager


def get_permissions(discord_id: int) -> list:
    """
    Returns list of permissions for a Discord user.

    :param discord_id: The Discord user ID of the respective user.
    :return: A list of the user's permissions.
    """
    with db_connect() as conn:
        cursor = conn.cursor()

        create_account(discord_id, cursor=cursor)

        cursor.execute(
            'SELECT permissions FROM accounts WHERE discord_id = ?', (discord_id,))
        permissions: tuple = cursor.fetchone()

    if permissions:
        return comma_separated_to_list(permissions[0])
    return []


def has_permission(
    discord_id: int,
    permissions: str | list[str],
    allow_star: bool=True
) -> bool:
    """
    Check if a user has one or more of the specified permissions.

    :param discord_id: The Discord user ID of the respective user.
    :param permissions: The permission(s) to check that the user has one more of.
    :param allow_star: Allow star (*) permission to overrule permission checks.
    :return bool: Whether the user has derived access to the specified permissions.
    """
    user_permissions = get_permissions(discord_id)

    if allow_star and '*' in user_permissions:
        return True

    if isinstance(permissions, str):
        permissions = [permissions]

    # at least one permission is in user_permissions
    if set(permissions) & set(user_permissions):
        return True

    return False


def set_permissions(discord_id: int, permissions: list | str) -> None:
    """
    Sets the user's permissions to the given set of permissions.
    This will completely override any existing permissions.

    :param discord_id: The Discord user ID of the respective user.
    :param permissions: The permissions either as a list, or comma seperated list.
    """
    if isinstance(permissions, list):
        permissions = ','.join(permissions)

    with db_connect() as conn:
        cursor = conn.cursor()

        cursor.execute(
            'SELECT account_id FROM accounts WHERE discord_id = ?', (discord_id,))
        existing_data: tuple = cursor.fetchone()

        if existing_data:
            cursor.execute(
                "UPDATE accounts SET permissions = ? WHERE discord_id = ?",
                (permissions, discord_id))
        else:
            create_account(discord_id, permissions=permissions, cursor=cursor)


def add_permission(discord_id: int, permission: str) -> None:
    """
    Adds a permission to a user if they don't already have it.

    :param discord_id: The Discord user ID of the respective user.
    :param permission: The permission to add to the user.
    """
    permissions = get_permissions(discord_id)

    if not permission in permissions:
        permissions.append(permission)
        set_permissions(discord_id, permissions)


def remove_permission(discord_id: int, permission: str) -> None:
    """
    Removes a permission from a user if they have it.

    :param discord_id: The Discord user ID of the respective user.
    :param permission: The permission to remove from the user.
    """
    permissions = get_permissions(discord_id)

    if permission in permissions:
        while permission in permissions:
            permissions.remove(permission)
        set_permissions(discord_id, permissions)


def has_access(
    discord_id: int, permissions: str | list[str], allow_star=True
) -> bool:
    """
    Check if a user's account has access to one or more of the
    specified permission(s), accounting for permissions derived
    from subscriptions.

    Similar to `has_permission` but accounts for subscription based permissions
    Returns bool `True` or `False` if a user has a permission
    :param discord_id: The Discord user ID of the respective user.
    :param permissions: The permission(s) to check that the user has one more of.
    :param allow_star: Allow star (*) permission to overrule permission checks.
    :return bool: Whether the user has derived access to the specified permissions.
    """
    if not discord_id:
        return False

    subscription = SubscriptionManager(discord_id).get_subscription()
    package_perms = subscription.package_permissions

    package_perms = set(package_perms)

    user_permissions = get_permissions(discord_id)

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


class PermissionManager:
    """A permissions manager for the account."""
    def __init__(self, discord_id: int):
        self.discord_id = discord_id


    def add_permission(self, permission: str):
        """
        Adds a permission to a user if they don't already have it.

        :param permission: The permission to add to the user.
        """
        add_permission(self.discord_id, permission)


    def remove_permission(self, permission: str):
        """
        Removes a permission from a user if they have it.

        :param permission: The permission to remove from the user.
        """
        remove_permission(self.discord_id, permission)


    def set_permissions(self, permissions: list | str):
        """
        Sets the user's permissions to the given set of permissions.
        This will completely override any existing permissions.

        :param permissions: The permissions either as a list, or comma seperated list.
        """
        set_permissions(self.discord_id, permissions)


    def get_permissions(self):
        """
        Returns a list of the user's permissions.

        :return list: A list of the user's permissions
        """
        return get_permissions(self.discord_id)


    def has_permission(self, permissions: str | list[str], allow_star: bool=True):
        """
        Check if a user has one or more of the specified permissions.

        :param permissions: The permission(s) to check that the user has one more of.
        :param allow_star: Allow star (*) permission to overrule permission checks.
        :return bool: Whether the user has derived access to the specified permissions.
        """
        return has_permission(self.discord_id, permissions, allow_star)


    def has_access(self, permissions: str | list[str], allow_star: bool=True):
        """
        Check if a user's account has access to one or more of the
        specified permission(s), accounting for permissions derived
        from subscriptions.

        :param permissions: The permission(s) to check that the user has one more of.
        :param allow_star: Allow star (*) permission to overrule permission checks.
        :return bool: Whether the user has derived access to the specified permissions.
        """
        return has_access(self.discord_id, permissions, allow_star)
