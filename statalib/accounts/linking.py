"""Functionality for linking Discord accounts to Hypixel accounts."""

from dataclasses import dataclass
from enum import Enum

import mcfetch

from ..aliases import HypixelData, PlayerName, PlayerUUID
from ..db import Cursor, ensure_cursor
from ..sessions import SessionManager
from ..usage import insert_growth_data
from .permissions import AccountPermissions


@ensure_cursor
def get_total_linked_accounts(*, cursor: Cursor = None) -> int:
    """Return the total linked accounts count."""
    cursor.execute("SELECT COUNT(discord_id) FROM linked_accounts")
    total = cursor.fetchone()

    if total:
        return total[0]
    return 0


@ensure_cursor
def uuid_to_discord_id(uuid: PlayerUUID, *, cursor: Cursor = None) -> int | None:
    """
    Attempt to retrieve the linked Discord ID that corresponds
    to a player UUID if there is one.

    :param uuid: The UUID of the player to find linked Discord ID for.
    :return int | None: The linked Discord ID if found, otherwise None.
    """
    discord_id = cursor.execute(
        "SELECT discord_id FROM linked_accounts WHERE uuid = ?", (uuid,)
    ).fetchone()

    return None if not discord_id else discord_id[0]


@dataclass
class LinkingOutcome:
    success: bool
    id: int
    
class LinkingOutcomeEnum(Enum):
    SUCCESS = LinkingOutcome(True, 0)
    SUCCESS_AND_SESSION_CREATED = LinkingOutcome(True, 1)
    NO_CONNECTION = LinkingOutcome(False, 2)
    CONNECTION_MISMATCH = LinkingOutcome(False, 3)


class AccountLinking:
    """Manager for account linking."""

    def __init__(self, discord_user_id: int) -> None:
        self._discord_user_id = discord_user_id

    @ensure_cursor
    def get_linked_player_uuid(self, *, cursor: Cursor = None) -> PlayerUUID | None:
        """Retrieve the player UUID linked to a user if there is one."""
        linked_data = cursor.execute(
            "SELECT * FROM linked_accounts WHERE discord_id = ?",
            (self._discord_user_id,),
        ).fetchone()

        if linked_data and linked_data[1]:
            return linked_data[1]
        return None

    @ensure_cursor
    def set_linked_player(self, uuid: PlayerUUID, *, cursor: Cursor = None) -> None:
        """
        Set the player linked to the user.

        :param uuid: The Minecraft player UUID of the respective player.
        """
        cursor.execute(
            "SELECT * FROM linked_accounts WHERE discord_id = ?",
            (self._discord_user_id,),
        )
        linked_data = cursor.fetchone()

        if not linked_data:
            cursor.execute(
                "INSERT INTO linked_accounts (discord_id, uuid) VALUES (?, ?)",
                (self._discord_user_id, uuid),
            )
        else:
            cursor.execute(
                "UPDATE linked_accounts SET uuid = ? WHERE discord_id = ?",
                (uuid, self._discord_user_id),
            )

        if not linked_data:
            insert_growth_data(self._discord_user_id, "add", "linked", cursor=cursor)

    @ensure_cursor
    def unlink_account(self, *, cursor: Cursor = None) -> str | None:
        """
        Unlink a user from a player.

        :return str | None: The formerly linked player UUID if there was one, \
            otherwise None.
        """
        current_data: tuple[str] | None = cursor.execute(
            "SELECT uuid FROM linked_accounts WHERE discord_id = ?",
            (self._discord_user_id,),
        ).fetchone()

        if current_data:
            _ = cursor.execute(
                "DELETE FROM linked_accounts WHERE discord_id = ?",
                (self._discord_user_id,),
            )

            insert_growth_data(self._discord_user_id, "remove", "linked", cursor=cursor)
            return current_data[0]

        return None

    @ensure_cursor
    def update_autofill(
        self, uuid: PlayerUUID, username: PlayerName, *, cursor: Cursor = None
    ) -> None:
        """
        Updates the username autocompletion option for a certain player.

        :param uuid: The linked player UUID of the target linked user.
        :param username: The updated linked player username of the target linked user.
        """
        perms = AccountPermissions(self._discord_user_id)
        if perms.has_access("autofill", cursor=cursor):
            autofill_data: tuple[int, str, str] | None = cursor.execute(
                "SELECT * FROM autofill WHERE discord_id = ?", (self._discord_user_id,)
            ).fetchone()

            if not autofill_data:
                query = (
                    "INSERT INTO autofill (discord_id, uuid, username) VALUES (?, ?, ?)"
                )
                _ = cursor.execute(query, (self._discord_user_id, uuid, username))
            elif autofill_data[2] != username:
                query = (
                    "UPDATE autofill SET uuid = ?, username = ? WHERE discord_id = ?"
                )
                _ = cursor.execute(query, (uuid, username, self._discord_user_id))

    @ensure_cursor
    def delete_all_autofill_data(self, *, cursor: Cursor = None) -> None:
        """
        Irreversibly delete all the user's autofill data.
        """
        _ = cursor.execute(
            "DELETE FROM autofill WHERE discord_id = ?", (self._discord_user_id,)
        )

    @ensure_cursor
    def link_account(
        self,
        discord_tag: str,
        hypixel_data: HypixelData,
        name: PlayerName,
        uuid: PlayerUUID,
        create_session: bool=True,
        *,
        cursor: Cursor = None,
    ) -> LinkingOutcomeEnum:
        """
        Attempt to link a Discord account to a Hypixel account.
        Either `uuid`, `name`, or both must be passed.

        :param discord_tag: The username of the Discord account.
        :param hypixel_data: The Hypixel data of the respective player.
        :param uuid: The player UUID of the Hypixel account to be linked.
        :param name: The player username of the Hypixel account to be linked.
        :param create_session: Whether to create a session if one doesn't already exist.
        :return LinkingOutcomeEnum: Info about whether status of the linking attempt.
        """
        if not hypixel_data.get("player"):
            return LinkingOutcomeEnum.NO_CONNECTION

        hypixel_discord_tag: str | None = (
            (hypixel_data.get("player") or {})
            .get("socialMedia", {})
            .get("links", {})
            .get("DISCORD", None)
        )

        if not hypixel_discord_tag:
            return LinkingOutcomeEnum.NO_CONNECTION

        if discord_tag != hypixel_discord_tag:
            return LinkingOutcomeEnum.CONNECTION_MISMATCH

        self.set_linked_player(uuid, cursor=cursor)
        self.update_autofill(uuid, name, cursor=cursor)

        if create_session:
            session_manager = SessionManager(uuid)
            if session_manager.session_count(cursor=cursor) == 0:
                session_manager.create_session(
                    session_id=1, hypixel_data=hypixel_data, cursor=cursor
                )
                return LinkingOutcomeEnum.SUCCESS_AND_SESSION_CREATED

        return LinkingOutcomeEnum.SUCCESS

    # FIXME
    @ensure_cursor
    def fetch_linked_player_name(self, *, cursor: Cursor = None) -> str | None:
        """Fetch the player username that corresponding with the linked player UUID."""
        linked_player_uuid = self.get_linked_player_uuid(cursor=cursor)

        if linked_player_uuid is not None:
            return mcfetch.Player(linked_player_uuid).name
        return None
