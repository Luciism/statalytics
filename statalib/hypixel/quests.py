"""Bedwars quests related functionality."""

from typing import TypedDict
from ..aliases import HypixelPlayerData

QUESTS_XP_MAP: dict[str, int | dict[int, int]] = {
    "bedwars_daily_win": 250,
    "bedwars_daily_one_more": {
        1683085688000: 250,
        0: 0
    },
    "bedwars_daily_gifts": 700,
    "bedwars_daily_nightmares": 1000,
    "bedwars_daily_final_killer": 250,
    "bedwars_daily_bed_breaker": 250,
    "bedwars_weekly_bed_elims": 5000,
    "bedwars_weekly_dream_win": 5000,
    "bedwars_weekly_challenges": 2500,
    "bedwars_weekly_pumpkinator": 6666,
    "bedwars_weekly_challenges_win": 5000,
    "bedwars_weekly_final_killer": 5000
}
"""Mappings of all quests to xp. If the quest gave different amounts of xp
at different times, it will be a dictionary mapped to a unix timestamp."""


class QuestDataDict(TypedDict):
    """Data for a specific quest."""
    completions: int
    experience: int

class QuestsExpDataDict(TypedDict):
    """Data for each type of quest."""
    bedwars_daily_win: QuestDataDict
    bedwars_daily_one_more: QuestDataDict
    bedwars_daily_gifts: QuestDataDict
    bedwars_daily_nightmares: QuestDataDict
    bedwars_daily_final_killer: QuestDataDict
    bedwars_daily_bed_breaker: QuestDataDict
    bedwars_weekly_bed_elims: QuestDataDict
    bedwars_weekly_dream_win: QuestDataDict
    bedwars_weekly_challenges: QuestDataDict
    bedwars_weekly_pumpkinator: QuestDataDict
    bedwars_weekly_challenges_win: QuestDataDict
    bedwars_weekly_final_killer: QuestDataDict

class QuestsDataDict(TypedDict):
    """Data for all quests."""
    quests_exp: QuestsExpDataDict
    real_exp: int
    total_quests_exp: int


def get_quests_data(hypixel_player_data: HypixelPlayerData) -> QuestsDataDict:
    """
    Get the total completions and XP gained for each quest.

    :param hypixel_player_data: The Hypixel response player data.
    """
    # Some comments would be nice.
    total_experience = hypixel_player_data.get(
        'stats', {}).get('Bedwars', {}).get('Experience', 0)

    quest_data = {'quests_exp': {}, 'completions': 0}
    xp_by_quests = 0

    for quest, exp in QUESTS_XP_MAP.items():
        if isinstance(exp, dict):
            quest_completions: list[dict] = hypixel_player_data.get(
                'quests', {}).get(quest, {}).get('completions', {})

            quest_data['completions'] += len(quest_completions)

            quest_exp = 0
            for completion in quest_completions:
                completed_timestamp = completion.get('time', 0)

                for timestamp, timestamp_exp in exp.items():
                    if completed_timestamp >= timestamp:
                        quest_exp += timestamp_exp

            xp_by_quests += quest_exp
            quest_data['quests_exp'].setdefault(
                quest, {})['completions'] = len(quest_completions)
            quest_data['quests_exp'][quest]['experience'] = quest_exp

        else:
            completions = len(hypixel_player_data.get(
                'quests', {}).get(quest, {}).get('completions', {}))

            quest_exp = completions * exp
            xp_by_quests += quest_exp

            quest_data['quests_exp'].setdefault(quest, {})['completions'] = completions
            quest_data['quests_exp'][quest]['experience'] = quest_exp
            quest_data['completions'] += completions

    quest_data['real_exp'] = total_experience - xp_by_quests
    quest_data['total_quests_exp'] = xp_by_quests

    return quest_data
