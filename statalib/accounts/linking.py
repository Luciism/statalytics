"""Functionality for linking Discord accounts to Hypixel accounts."""

from .permissions import AccountPermissions
from ..mcfetch import AsyncFetchPlayer, FetchPlayer2
from ..sessions import SessionManager
from ..aliases import PlayerName, PlayerUUID, HypixelData
from ..functions import insert_growth_data
from ..db import db_connect


def get_total_linked_accounts() -> int:
    """Return the total linked accounts count."""
    with db_connect() as conn:
        cursor = conn.cursor()

        cursor.execute(f"SELECT COUNT(discord_id) FROM linked_accounts")
        total = cursor.fetchone()
    if total:
        return total[0]
    return 0


def uuid_to_discord_id(uuid: PlayerUUID) -> int | None:
    """
    Attempt to retrieve the linked Discord ID that corresponds
    to a player UUID if there is one.

    :param uuid: The UUID of the player to find linked Discord ID for.
    :return int | None: The linked Discord ID if found, otherwise None.
    """
    with db_connect() as conn:
        cursor = conn.cursor()

        cursor.execute(
            f"SELECT discord_id FROM linked_accounts WHERE uuid = '{uuid}'")
        discord_id = cursor.fetchone()

    return None if not discord_id else discord_id[0]



class AccountLinking:
    """Manager for account linking."""
    def __init__(self, discord_user_id: int) -> None:
        self._discord_user_id = discord_user_id

    def get_linked_player_uuid(self) -> PlayerUUID | None:
        """Retrieve the player UUID linked to a user if there is one."""
        with db_connect() as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"SELECT * FROM linked_accounts WHERE discord_id = ?",
                (self._discord_user_id,))
            linked_data = cursor.fetchone()

        if linked_data and linked_data[1]:
            return linked_data[1]
        return None

    def set_linked_player(self, uuid: PlayerUUID) -> None:
        """
        Set the player linked to the user.

        :param uuid: The Minecraft player UUID of the respective player.
        """
        with db_connect() as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"SELECT * FROM linked_accounts WHERE discord_id = ?",
                (self._discord_user_id,))
            linked_data = cursor.fetchone()

            if not linked_data:
                cursor.execute(
                    "INSERT INTO linked_accounts (discord_id, uuid) VALUES (?, ?)",
                    (self._discord_user_id, uuid))
            else:
                cursor.execute(
                    "UPDATE linked_accounts SET uuid = ? WHERE discord_id = ?",
                    (uuid, self._discord_user_id))

        if not linked_data:
            insert_growth_data(self._discord_user_id, 'add', 'linked')

    def unlink_account(self) -> str | None:
        """
        Unlink a user from a player.

        :return str | None: The formerly linked player UUID if there was one, \
            otherwise None.
        """
        with db_connect() as conn:
            cursor = conn.cursor()

            cursor.execute(
                "SELECT uuid FROM linked_accounts WHERE discord_id = ?",
                (self._discord_user_id,))
            current_data = cursor.fetchone()

            if current_data:
                cursor.execute(
                    "DELETE FROM linked_accounts WHERE discord_id = ?", (self._discord_user_id,))

        if current_data:
            insert_growth_data(self._discord_user_id, 'remove', 'linked')
            return current_data[0]
        return None


    def update_autofill(self, uuid: PlayerUUID, username: PlayerName) -> None:
        """
        Updates the username autocompletion option for a certain player.

        :param uuid: The linked player UUID of the target linked user.
        :param username: The updated linked player username of the target linked user.
        """
        if AccountPermissions(self._discord_user_id).has_access('autofill'):
            with db_connect() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    f"SELECT * FROM autofill WHERE discord_id = ?", (self._discord_user_id,))
                autofill_data: tuple = cursor.fetchone()

                if not autofill_data:
                    query = "INSERT INTO autofill (discord_id, uuid, username) VALUES (?, ?, ?)"
                    cursor.execute(query, (self._discord_user_id, uuid, username))
                elif autofill_data[2] != username:
                    query = "UPDATE autofill SET uuid = ?, username = ? WHERE discord_id = ?"
                    cursor.execute(query, (uuid, username, self._discord_user_id))

    async def link_account(
        self,
        discord_tag: str,
        hypixel_data: HypixelData,
        name: PlayerName=None,
        uuid: PlayerUUID=None
    ) -> int:
        """
        Attempt to link a Discord account to a Hypixel account.
        Either `uuid`, `name`, or both must be passed.

        :param discord_tag: The Discord user's tag (with or without a discriminator).
        :param hypixel_data: The Hypixel data of the respective player.
        :param uuid: The player UUID of the Hypixel account to be linked.
        :param name: The player username of the Hypixel account to be linked.
        :return int: 2 - Linking was a success AND a session was created, \
            1 - Linking was a success, \
            0 - Discord tags don't match, \
            -1 - Discord tag isn't set
        """
        if discord_tag.endswith('#0'):
            discord_tag = discord_tag[:-2]

        if not hypixel_data.get('player'):
            return -1

        hypixel_discord_tag: str = (hypixel_data.get('player') or {}).get(
            'socialMedia', {}).get('links', {}).get('DISCORD', None)

        # Linking Logic
        if hypixel_discord_tag:
            if discord_tag == hypixel_discord_tag:
                if not name:
                    name = await AsyncFetchPlayer(uuid=uuid).name

                self.set_linked_player(uuid)
                self.update_autofill(uuid, name)

                session_manager = SessionManager(uuid)
                if session_manager.session_count() == 0:
                    session_manager.create_session(session_id=1, hypixel_data=hypixel_data)
                    return 2
                return 1
            return 0
        return -1


    def fetch_linked_player_name(self) -> str | None:
        """Fetch the player username that corresponding with the linked player UUID."""
        linked_player_uuid = self.get_linked_player_uuid()

        if linked_player_uuid is not None:
            return FetchPlayer2(linked_player_uuid).name
        return None
