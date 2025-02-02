"""Rotational stats related types."""

from datetime import datetime
from enum import Enum

from ..stats_snapshot import BedwarsStatsSnapshot


class RotationType(Enum):
    """Rotational types."""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"

    @staticmethod
    def from_string(string: str) -> 'RotationType':
        """Convert a string to a rotational type."""
        attributes = {r.value: r.name for r in RotationType}
        return RotationType.__getattribute__(RotationType, attributes.get(string))


class BedwarsRotation:
    """Bedwars rotational data."""
    def __init__(
        self,
        rotation_info: dict,
        rotation_data: BedwarsStatsSnapshot
    ) -> None:
        """
        Initialize the class.

        :param rotational_info: Information about the rotational data.
        :param rotation_data: The rotational data.
        """
        self.uuid: str = rotation_info["uuid"]
        "The UUID of the player."
        self.rotation = RotationType.from_string(rotation_info["rotation"])
        "The type of rotation; daily, weekly, monthly, etc."
        self.last_reset_timestamp: float = rotation_info["last_reset_timestamp"]
        "The UTC timestamp of the last reset."
        self.snapshot_id: str = rotation_info["snapshot_id"]
        "The unique snapshot ID."

        self.data = rotation_data
        "The bedwars stats snapshot data."


class BedwarsHistoricalRotation:
    """Historical rotational data of past rotations."""
    def __init__(
        self,
        historic_info: dict,
        historic_data: BedwarsStatsSnapshot
    ) -> None:
        """
        Initialize the class.

        :param historic_info: Information about the historic rotational data.
        :param historic_data: The historic rotational data.
        """
        self.uuid: str = historic_info["uuid"]
        "The UUID of the player."
        self.period_id: str = historic_info["period_id"]
        "An ID representing which day, week, month, or year the stats were taken from."
        self.level: int = historic_info["level"]
        "The bedwars level of the player at the time of the snapshot."
        self.snapshot_id: str = historic_info["snapshot_id"]
        "The unique snapshot ID."

        self.data = historic_data
        "The bedwars stats snapshot data."


class HistoricalRotationPeriodID:
    """Represents the specific day, week, month,
    or year that the stats were taken from."""
    def __init__(
        self,
        rotation_type: RotationType,
        datetime_info: datetime
    ) -> None:
        """
        Initialize the class.

        :param rotation_type: The type of rotation; daily, weekly, monthly, etc.
        :param datetime_info: A datetime object that reflects the time of the snapshot.
        """
        self.rotation_type = rotation_type
        self.datetime_info = datetime_info

    def to_string(self) -> str:
        """Format the period ID into a string"""
        format_map = {
            "daily": "daily_%Y_%m_%d",
            "weekly": "weekly_%Y_%U",
            "monthly": "monthly_%Y_%m",
            "yearly": "yearly_%Y"
        }
        return self.datetime_info.strftime(format_map[self.rotation_type.value])
