from ...aliases import HypixelPlayerData
from ..leveling import Leveling
from ...render.prestige_colors import Prestige


class BedwarsQualifyingValueFormatter:
    def __init__(self, player_data: HypixelPlayerData) -> None:
        self._player_data: HypixelPlayerData = player_data

    def bedwars_level(self) -> str:
        try:
            xp: int = self._player_data["stats"]["Bedwars"]["Experience"]
        except KeyError:
            xp = 0

        formatted_level = Prestige.format_level(int(Leveling(xp).level))
        return formatted_level

    def final_kills_new(self) -> str:
        """Overall Final Kills"""
        try:
            final_kills: int = self._player_data["stats"]["Bedwars"]["final_kills_bedwars"]
        except KeyError:
            final_kills = 0

        return f"{final_kills:,}"

    def wins_new(self) -> str:
        """Overall Wins"""
        try:
            wins: int = self._player_data["stats"]["Bedwars"]["wins_bedwars"]
        except KeyError:
            wins = 0

        return f"{wins:,}"

    def call_formatter(self, name: str) -> str:
        return self.__getattribute__(name)()

