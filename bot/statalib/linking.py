import sqlite3

from .mcfetch import AsyncFetchPlayer
from .sessions import start_session, find_dynamic_session
from .permissions import has_access
from .aliases import PlayerName, PlayerUUID
from .functions import insert_growth_data
from .common import REL_PATH


def get_linked_total() -> int:
    """Returns total linked accounts"""
    with sqlite3.connect(f'{REL_PATH}/database/core.db') as conn:
        cursor = conn.cursor()

        cursor.execute(f"SELECT COUNT(discord_id) FROM linked_accounts")
        total = cursor.fetchone()
    if total:
        return total[0]
    return 0


def uuid_to_discord_id(uuid: PlayerUUID) -> int | None:
    """
    Attempts to fetch discord id from linked database
    :param uuid: The uuid of the player to find linked data for
    """
    with sqlite3.connect(f'{REL_PATH}/database/core.db') as conn:
        cursor = conn.cursor()

        cursor.execute(
            f"SELECT discord_id FROM linked_accounts WHERE uuid = '{uuid}'")
        discord_id = cursor.fetchone()

    return None if not discord_id else discord_id[0]


def get_linked_player(discord_id: int) -> PlayerUUID | None:
    """
    Returns a users linked player uuid from database
    :param discord_id: The discord id of user's linked data to be retrieved
    """
    with sqlite3.connect(f'{REL_PATH}/database/core.db') as conn:
        cursor = conn.cursor()
        cursor.execute(
            f"SELECT * FROM linked_accounts WHERE discord_id = {discord_id}")
        linked_data = cursor.fetchone()

    if linked_data and linked_data[1]:
        return linked_data[1]
    return None


def set_linked_data(discord_id: int, uuid: PlayerUUID) -> None:
    """
    Inserts linked account data into database
    :param discord_id: the discord id of the respective user
    :param uuid: the minecraft uuid of the relvative user
    """
    with sqlite3.connect(f'{REL_PATH}/database/core.db') as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM linked_accounts WHERE discord_id = {discord_id}")
        linked_data = cursor.fetchone()

        if not linked_data:
            cursor.execute(
                "INSERT INTO linked_accounts (discord_id, uuid) VALUES (?, ?)",
                (discord_id, uuid))
        else:
            cursor.execute(
                "UPDATE linked_accounts SET uuid = ? WHERE discord_id = ?",
                (uuid, discord_id))

    if not linked_data:
        insert_growth_data(discord_id, 'add', 'linked')


def delete_linked_data(discord_id: int) -> bool:
    """
    Unlinks a discord user from a player
    :param discord_id: the discord id of the respective user
    :returns: former linked uuid of the discord user if the user
    was already linked and able to be unlinked otherwise `None`
    """
    with sqlite3.connect(f'{REL_PATH}/database/core.db') as conn:
        cursor = conn.cursor()

        cursor.execute(
            "SELECT uuid FROM linked_accounts WHERE discord_id = ?", (discord_id,))
        current_data = cursor.fetchone()

        if current_data:
            cursor.execute(
                "DELETE FROM linked_accounts WHERE discord_id = ?", (discord_id,))

    if current_data:
        insert_growth_data(discord_id, 'remove', 'linked')
        return current_data[0]
    return None


def update_autofill(
    discord_id: int,
    uuid: PlayerUUID,
    username: PlayerName
) -> None:
    """
    Updates autofill for a user, this will be helpful if a user has changed their ign
    :param discord_id: The discord id of the target linked user
    :param uuid: The uuid of the target linked user
    :param username: The updated username of the target linked user
    """
    if has_access(discord_id, 'autofill'):
        with sqlite3.connect(f'{REL_PATH}/database/core.db') as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM autofill WHERE discord_id = {discord_id}")
            autofill_data: tuple = cursor.fetchone()

            if not autofill_data:
                query = "INSERT INTO autofill (discord_id, uuid, username) VALUES (?, ?, ?)"
                cursor.execute(query, (discord_id, uuid, username))
            elif autofill_data[2] != username:
                query = "UPDATE autofill SET uuid = ?, username = ? WHERE discord_id = ?"
                cursor.execute(query, (uuid, username, discord_id))


async def link_account(
    discord_tag: str,
    discord_id: int,
    hypixel_data: dict,
    uuid: PlayerUUID=None,
    name: PlayerName=None
) -> bool | None:
    """
    Attempt to link an discord account to a hypixel account
    :param discord_tag: The discord user's full tag eg: Example#1234
    :param discord_id: The discord user's id
    :param hypixel_data: the hypixel data of the player
    :param uuid: The uuid of the hypixel account being linked
    :param name: The username of the hypixel account being linked

    Either uuid, name, or both must be passed

    #### Returns:
        2 - linking was a success and session was created\n
        1 - linking was a success\n
        0 - discord tags don't match\n
        -1 - discord tag isn't set\n
    """
    if discord_tag.endswith('#0'):
        discord_tag = discord_tag[:-2]

    if not hypixel_data.get('player'):
        return -1

    hypixel_discord_tag: str = hypixel_data.get('player', {}).get(
        'socialMedia', {}).get('links', {}).get('DISCORD', None)

    # Linking Logic
    if hypixel_discord_tag:
        if discord_tag == hypixel_discord_tag:
            if not name:
                name = await AsyncFetchPlayer(uuid=uuid).name

            set_linked_data(discord_id, uuid)
            update_autofill(discord_id, uuid, name)

            if not find_dynamic_session(uuid):
                await start_session(uuid, session=1, hypixel_data=hypixel_data)
                return 2
            return 1
        return 0
    return -1


class LinkingManager:
    def __init__(self, discord_id: int):
        self._discord_id = discord_id


    def get_linked_player(self):
        """
        Returns a users linked data from linked database
        """
        return get_linked_player(self._discord_id)


    def set_linked_data(self, uuid: PlayerUUID):
        """
        Inserts linked account data into database
        :param uuid: the minecraft uuid of the relvative user
        """
        set_linked_data(self._discord_id, uuid)


    def delete_linked_data(self) -> bool:
        """
        Unlinks the discord user from a player
        :returns: former linked uuid of the discord user if the user
        was already linked and able to be unlinked otherwise `None`
        """
        delete_linked_data(self._discord_id)


    def uuid_to_discord_id(self, uuid: PlayerUUID):
        """
        Attempts to fetch discord id from linked database
        :param uuid: The uuid of the player to find linked data for
        """
        return uuid_to_discord_id(uuid)


    def update_autofill(self, uuid: PlayerUUID, username: PlayerName):
        """
        Updates autofill for a user, this will be helpful if a user has changed their ign
        :param uuid: The uuid of the target linked user
        :param username: The updated username of the target linked user
        """
        update_autofill(self._discord_id, uuid, username)


    async def link_account(
        self,
        discord_tag: str,
        hypixel_data: dict,
        name: PlayerName=None,
        uuid: PlayerUUID=None
    ):
        """
        Attempt to link an discord account to a hypixel account
        :param discord_tag: The discord user's full tag eg: Example#1234
        :param hypixel_data: the hypixel data of the player
        :param uuid: The uuid of the hypixel account being linked
        :param name: The username of the hypixel account being linked

        Either uuid, name, or both must be passed

        #### Returns:
            2 - linking was a success and session was created\n
            1 - linking was a success\n
            0 - discord tags don't match\n
            -1 - discord tag isn't set\n
        """
        response = await link_account(
            discord_tag, self._discord_id, hypixel_data, uuid, name)
        return response
