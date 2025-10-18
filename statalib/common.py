"""Common constants and functions."""

from dataclasses import dataclass
from enum import Enum
import os
from datetime import datetime, UTC


REL_PATH = os.path.abspath(f'{__file__}/../..')
"The base path of the project."

class _MissingSentinel:  # Thanks discord.py
    """A sentinel object to represent the absence of a value."""
    __slots__ = ()
    def __eq__(self, other) -> bool:
        return False
    def __bool__(self) -> bool:
        return False
    def __hash__(self) -> int:
        return 0
    def __repr__(self):
        return '...'

MISSING = _MissingSentinel()
"Global missing sentinel instance."

def utc_now() -> datetime:
    """Get the current UTC datetime."""
    return datetime.now(UTC)


@dataclass
class Mode:
    name: str
    id: str
    prefix: str | list[str]
    is_dream: bool = True 
    is_real: bool = True

    @property
    def is_compound(self) -> bool:
        return isinstance(self.prefix, list)

class ModesEnum(Enum):
    OVERALL = Mode("Overall", "overall", "", is_dream=False, is_real=False)
    SOLOS = Mode("Solos", "solos", "eight_one_", is_dream=False)
    DOUBLES = Mode("Doubles", "doubles", "eight_two_", is_dream=False)
    THREES = Mode("Threes", "threes", "four_three_", is_dream=False)
    FOURS = Mode("Fours", "fours", "four_four_", is_dream=False)
    FOUR_VS_FOUR = Mode("4v4", "four_vs_four", "two_four_", is_dream=False)

    DREAMS_OVERALL = Mode("Dreams Overall", "dreams_overall", [
        "eight_two_voidless_",
        "four_four_voidless_",
        "eight_two_swap_",
        "four_four_swap_",
        "eight_two_oneblock_",
        "four_four_oneblock_",
        "eight_two_lucky_",
        "four_four_lucky_",
        "eight_two_rush_",
        "four_four_rush_",
        "eight_two_ultimate_",
        "four_four_ultimate_",
        "castle_"
    ], is_real=False) 


    DREAMS_VOIDLESS = Mode("Voidless", "voidless", ["eight_two_voidless_", "four_four_voidless_"], is_real=False) 
    DREAMS_VOIDLESS_DOUBLES = Mode("Voidless Doubles", "voidless_doubles", "eight_two_voidless_") 
    DREAMS_VOIDLESS_FOURS = Mode("Voidless Fours", "voidless_fours", "four_four_voidless_") 

    DREAMS_SWAP = Mode("Swap", "swap", ["eight_two_swap_", "four_four_swap_"], is_real=False)
    DREAMS_SWAP_DOUBLES = Mode("Swap Doubles", "swap_doubles", "eight_two_swap_") 
    DREAMS_SWAP_FOURS = Mode("Swap Fours", "swap_fours", "four_four_swap_") 

    DREAMS_ONEBLOCK = Mode("One Block", "oneblock", "eight_one_oneblock_") 

    DREAMS_LUCKY = Mode("Lucky", "lucky", ["eight_two_lucky_", "four_four_lucky_"], is_real=False)
    DREAMS_LUCKY_DOUBLES = Mode("Lucky Doubles", "lucky_doubles", "eight_two_lucky_") 
    DREAMS_LUCKY_FOURS = Mode("Lucky Fours", "lucky_fours", "four_four_lucky_") 

    DREAMS_RUSH = Mode("Rush", "rush", ["eight_two_rush_", "four_four_rush_"], is_real=False)
    DREAMS_RUSH_DOUBLES = Mode("Rush Doubles", "rush_doubles", "eight_two_rush_") 
    DREAMS_RUSH_FOURS = Mode("Rush Fours", "rush_fours", "four_four_rush_") 

    DREAMS_ULTIMATE = Mode("Ultimate", "ultimate", ["eight_two_ultimate_", "four_four_ultimate_"], is_real=False)
    DREAMS_ULTIMATE_DOUBLES = Mode("Ultimate Doubles", "ultimate_doubles", "eight_two_ultimate_") 
    DREAMS_ULTIMATE_FOURS = Mode("Ultimate Fours", "ultimate_fours", "four_four_ultimate_") 

    DREAMS_CASTLE = Mode("Castle 40v40", "castle", "castle_")


    @staticmethod
    def core_modes(include_overall: bool=False) -> list[Mode]:
        modes = [
            ModesEnum.SOLOS.value,
            ModesEnum.DOUBLES.value,
            ModesEnum.THREES.value,
            ModesEnum.FOURS.value,
        ]
        if include_overall:
            modes.insert(0, ModesEnum.OVERALL.value)

        return modes

    @staticmethod
    def non_dream_modes() -> list[Mode]:
        return [mode.value for mode in ModesEnum if not mode.value.is_dream]

    @staticmethod
    def dream_modes() -> list[Mode]:
        return [mode.value for mode in ModesEnum if mode.value.is_dream]

    @staticmethod
    def get_mode_by_id(id: str) -> Mode | None:
        for mode in ModesEnum:
            if mode.value.id == id:
                return mode.value

