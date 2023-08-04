import sqlite3

from .functions import REL_PATH


def get_permissions(discord_id: int) -> list:
    """
    Returns list of permissions for a discord user
    :param discord_id: the discord id of the respective user
    """
    with sqlite3.connect(f'{REL_PATH}/database/core.db') as conn:
        cursor = conn.cursor()

        cursor.execute(
            'SELECT * FROM permissions WHERE discord_id = ?', (discord_id,))
        permissions: tuple = cursor.fetchone()

    if permissions and permissions[1]:
        return permissions[1].split(',')
    return []


def has_permission(discord_id: int, permission: str,
                   allow_star: bool=True) -> bool:
    """
    Returns bool `True` or `False` if a user has a permission
    :param discord_id: the discord id of the respective user
    :param permission: the permission to check for
    :param allow_star: returns `True` if the user has the `*` permission
    """
    permissions = get_permissions(discord_id)

    if allow_star and '*' in permissions:
        return True

    if permission in permissions:
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
            'SELECT discord_id FROM permissions WHERE discord_id = ?', (discord_id,))
        existing_data: tuple = cursor.fetchone()

        if existing_data:
            cursor.execute(
                "UPDATE permissions SET permissions = ? WHERE discord_id = ?",
                (permissions, discord_id))
        else:
            cursor.execute(
                "INSERT INTO permissions (discord_id, permissions) VALUES (?, ?)",
                (discord_id, permissions))


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


    def has_permission(self, permission: str, allow_star: bool=True):
        """
        Returns bool `True` or `False` if a user has a permission
        :param permission: the permission to check for
        :param allow_star: returns `True` if the user has the `*` permission
        """
        return has_permission(self.discord_id, permission, allow_star)
