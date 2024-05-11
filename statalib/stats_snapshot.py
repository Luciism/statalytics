from dataclasses import dataclass
import sqlite3


BEDWARS_STATS_SNAPSHOT_KEYS = [
    "Experience",
    "wins_bedwars",
    "losses_bedwars",
    "final_kills_bedwars",
    "final_deaths_bedwars",
    "kills_bedwars",
    "deaths_bedwars",
    "beds_broken_bedwars",
    "beds_lost_bedwars",
    "games_played_bedwars",
    "eight_one_wins_bedwars",
    "eight_one_losses_bedwars",
    "eight_one_final_kills_bedwars",
    "eight_one_final_deaths_bedwars",
    "eight_one_kills_bedwars",
    "eight_one_deaths_bedwars",
    "eight_one_beds_broken_bedwars",
    "eight_one_beds_lost_bedwars",
    "eight_one_games_played_bedwars",
    "eight_two_wins_bedwars",
    "eight_two_losses_bedwars",
    "eight_two_final_kills_bedwars",
    "eight_two_final_deaths_bedwars",
    "eight_two_kills_bedwars",
    "eight_two_deaths_bedwars",
    "eight_two_beds_broken_bedwars",
    "eight_two_beds_lost_bedwars",
    "eight_two_games_played_bedwars",
    "four_three_wins_bedwars",
    "four_three_losses_bedwars",
    "four_three_final_kills_bedwars",
    "four_three_final_deaths_bedwars",
    "four_three_kills_bedwars",
    "four_three_deaths_bedwars",
    "four_three_beds_broken_bedwars",
    "four_three_beds_lost_bedwars",
    "four_three_games_played_bedwars",
    "four_four_wins_bedwars",
    "four_four_losses_bedwars",
    "four_four_final_kills_bedwars",
    "four_four_final_deaths_bedwars",
    "four_four_kills_bedwars",
    "four_four_deaths_bedwars",
    "four_four_beds_broken_bedwars",
    "four_four_beds_lost_bedwars",
    "four_four_games_played_bedwars",
    "two_four_wins_bedwars",
    "two_four_losses_bedwars",
    "two_four_final_kills_bedwars",
    "two_four_final_deaths_bedwars",
    "two_four_kills_bedwars",
    "two_four_deaths_bedwars",
    "two_four_beds_broken_bedwars",
    "two_four_beds_lost_bedwars",
    "two_four_games_played_bedwars",
    "items_purchased_bedwars",
    "eight_one_items_purchased_bedwars",
    "eight_two_items_purchased_bedwars",
    "four_three_items_purchased_bedwars",
    "four_four_items_purchased_bedwars",
    "two_four_items_purchased_bedwars"
]


@dataclass
class BedwarsStatsSnapshot:
    snapshot_id: str
    experience: int
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


def get_snapshot_data(
    cursor: sqlite3.Cursor,
    snapshot_info: tuple
) -> tuple[dict, BedwarsStatsSnapshot]:
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
