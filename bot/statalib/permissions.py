import sqlite3

from .functions import comma_separated_to_list
from .common import REL_PATH
from .subscriptions_old import get_subscription, get_package_permissions
from .accounts import create_account


def get_permissions(discord_id: int) -> list:
    """
    Returns list of permissions for a discord user
    :param discord_id: the discord id of the respective user
    """
    with sqlite3.connect(f'{REL_PATH}/database/core.db') as conn:
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
    Returns bool `True` or `False` if a user has a permission
    :param discord_id: the discord id of the respective user
    :param permissions: the permission(s) to check for. if multiple permissions
        are provided, `True` will be returned if the user has
        at least one of the given permissions.
    :param allow_star: returns `True` if the user has the `*` permission
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


def set_permissions(discord_id: int, permissions: list | str):
    """
    Sets a users permissions to the given permissions\n
    Permissions can either be a list of permissions as a list
    or as a string with commas `,` as seperators
    :param discord_id: the discord id of the respective user
    :param permissions: the permissions to set for the user
    """
    if isinstance(permissions, list):
        permissions = ','.join(permissions)

    with sqlite3.connect(f'{REL_PATH}/database/core.db') as conn:
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


def add_permission(discord_id: int, permission: str):
    """
    Adds a permission to a user if they don't already have it
    :param discord_id: the discord id of the respective user
    :param permission: the permission to add to the user
    """
    permissions = get_permissions(discord_id)

    if not permission in permissions:
        permissions.append(permission)
        set_permissions(discord_id, permissions)


def remove_permission(discord_id: int, permission: str):
    """
    Removes a permission for a user if they have it
    :param discord_id: the discord id of the respective user
    :param permission: the permission to remove from the user
    """
    permissions = get_permissions(discord_id)

    if permission in permissions:
        while permission in permissions:
            permissions.remove(permission)
        set_permissions(discord_id, permissions)


def has_access(
    discord_id: int,
    permissions: str | list[str],
    allow_star=True
):
    """
    Similar to `has_permission` but accounts for subscription based permissions
    Returns bool `True` or `False` if a user has a permission
    :param discord_id: the discord id of the respective user
    :param permissions: the permission(s) to check for. if multiple permissions
        are provided, `True` will be returned if the user has
        at least one of the given permissions.
    :param allow_star: returns `True` if the user has the `*` permission
    """
    if not discord_id:
        return False

    subscription = get_subscription(discord_id)
    package_perms = get_package_permissions(subscription)

    package_perms = set(package_perms)

    user_permissions = get_permissions(discord_id)

    for user_permission in user_permissions:
        package_perms.add(user_permission)

    if '*' in package_perms and allow_star:
        return True

    if isinstance(permissions, str):
        permissions = [permissions]

    # user has at least one of the following permissions
    if set(permissions) & package_perms:
        return True

    return False


class PermissionManager:
    def __init__(self, discord_id: int):
        self.discord_id = discord_id


    def add_permission(self, permission: str):
        """
        Adds a permission to a user if they don't already have it
        :param permission: the permission to add to the user
        """
        add_permission(self.discord_id, permission)


    def remove_permission(self, permission: str):
        """
        Removes a permission for a user if they have it
        :param permission: the permission to remove from the user
        """
        remove_permission(self.discord_id, permission)


    def set_permissions(self, permissions: list | str):
        """
        Sets a users permissions to the given permissions\n
        Permissions can either be a list of permissions as a list
        or as a string with commas `,` as seperators
        :param permissions: the permissions to set for the user
        """
        set_permissions(self.discord_id, permissions)


    def get_permissions(self):
        """Returns list of permissions for a discord user"""
        return get_permissions(self.discord_id)


    def has_permission(self, permissions: str | list[str], allow_star: bool=True):
        """
        Returns bool `True` or `False` if a user has a permission
        :param permission: the permission to check for
        :param allow_star: returns `True` if the user has the `*` permission
        """
        return has_permission(self.discord_id, permissions, allow_star)


    def has_access(self, permissions: str | list[str], allow_star: bool=True):
        """
        Similar to `has_permission` but accounts for subscription based permissions
        Returns bool `True` or `False` if a user has a permission
        :param permissions: the permission(s) to check for. if multiple permissions
            are provided, `True` will be returned if the user has
            at least one of the given permissions.
        :param allow_star: returns `True` if the user has the `*` permission
        """
        return has_access(self.discord_id, permissions, allow_star)
