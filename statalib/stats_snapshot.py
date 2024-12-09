"""Bedwars stats snapshot dataclass and related functionality."""

from dataclasses import dataclass
import sqlite3

from .db import ensure_cursor


@dataclass
class BedwarsStatsSnapshot:
    """Bedwars stats snapshot dataclass."""
    snapshot_id: str
    Experience: int  # pylint: disable=invalid-name
    wins_bedwars: int
    losses_bedwars: int
    final_kills_bedwars: int
    final_deaths_bedwars: int
    kills_bedwars: int
    deaths_bedwars: int
    beds_broken_bedwars: int
    beds_lost_bedwars: int
    games_played_bedwars: int
    eight_one_wins_bedwars: int
    eight_one_losses_bedwars: int
    eight_one_final_kills_bedwars: int
    eight_one_final_deaths_bedwars: int
    eight_one_kills_bedwars: int
    eight_one_deaths_bedwars: int
    eight_one_beds_broken_bedwars: int
    eight_one_beds_lost_bedwars: int
    eight_one_games_played_bedwars: int
    eight_two_wins_bedwars: int
    eight_two_losses_bedwars: int
    eight_two_final_kills_bedwars: int
    eight_two_final_deaths_bedwars: int
    eight_two_kills_bedwars: int
    eight_two_deaths_bedwars: int
    eight_two_beds_broken_bedwars: int
    eight_two_beds_lost_bedwars: int
    eight_two_games_played_bedwars: int
    four_three_wins_bedwars: int
    four_three_losses_bedwars: int
    four_three_final_kills_bedwars: int
    four_three_final_deaths_bedwars: int
    four_three_kills_bedwars: int
    four_three_deaths_bedwars: int
    four_three_beds_broken_bedwars: int
    four_three_beds_lost_bedwars: int
    four_three_games_played_bedwars: int
    four_four_wins_bedwars: int
    four_four_losses_bedwars: int
    four_four_final_kills_bedwars: int
    four_four_final_deaths_bedwars: int
    four_four_kills_bedwars: int
    four_four_deaths_bedwars: int
    four_four_beds_broken_bedwars: int
    four_four_beds_lost_bedwars: int
    four_four_games_played_bedwars: int
    two_four_wins_bedwars: int
    two_four_losses_bedwars: int
    two_four_final_kills_bedwars: int
    two_four_final_deaths_bedwars: int
    two_four_kills_bedwars: int
    two_four_deaths_bedwars: int
    two_four_beds_broken_bedwars: int
    two_four_beds_lost_bedwars: int
    two_four_games_played_bedwars: int
    items_purchased_bedwars: int
    eight_one_items_purchased_bedwars: int
    eight_two_items_purchased_bedwars: int
    four_three_items_purchased_bedwars: int
    four_four_items_purchased_bedwars: int
    two_four_items_purchased_bedwars: int

    def as_tuple(self, include_snapshot_id: bool=True) -> tuple:
        """
        Convert the dataclass to a tuple.

        :param include_snapshot_id: Whether or not to include the snapshot ID.
        :return tuple: A tuple containing the snapshot data.
        """
        result = tuple(self.__dict__.values())

        if include_snapshot_id is False:
            # Remove snapshot ID
            result = result[1:]
        return result

    def as_dict(self, include_snapshot_id: bool=True) -> dict:
        """
        Convert the dataclass to a dictionary.

        :param include_snapshot_id: Whether or not to include the snapshot ID.
        :return dict: A dictionary containing the snapshot data.
        """
        result = self.__dict__

        if include_snapshot_id is False:
            result.pop("snapshot_id")
        return result

    @staticmethod
    def keys(include_snapshot_id: bool=True) -> list[str]:
        """
        Get the list of keys for the dataclass.

        :param include_snapshot_id: Whether or not to include the snapshot ID.
        :return list: A list of keys for the dataclass.
        """
        keys = list(BedwarsStatsSnapshot.__annotations__.keys())

        if include_snapshot_id is False:
            keys.remove("snapshot_id")  # Remove snapshot_id property

        return keys


@ensure_cursor
def get_snapshot_data(
    snapshot_info: tuple,
    *, cursor: sqlite3.Cursor=None
) -> tuple[dict, BedwarsStatsSnapshot]:
    """
    Retrieve the snapshot data for a specific snapshot ID.

    :param cursor: A custom `sqlite3.Cursor` object to operate on.
    :param snapshot_info: A tuple containing the raw snapshot info.
    :return tuple: A tuple containing the snapshot info and snapshot data.
    """
    column_names = [col[0] for col in cursor.description]
    snapshot_info_dict = dict(zip(column_names, snapshot_info))

    snapshot_id = snapshot_info_dict["snapshot_id"]
    cursor.execute(
        "SELECT * FROM bedwars_stats_snapshots WHERE snapshot_id = ?", (snapshot_id,))
    rotation_data: tuple | None = cursor.fetchone()

    if rotation_data is None:
        # Raise snapshot data missing error instead
        raise NotImplementedError("Data missing")

    snapshot_data = BedwarsStatsSnapshot(*rotation_data)
    return snapshot_info_dict, snapshot_data
