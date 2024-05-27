from datetime import datetime
from enum import Enum

from ..stats_snapshot import BedwarsStatsSnapshot


class RotationType(Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"

    @staticmethod
    def from_string(string: str) -> 'RotationType':
        attributes = {r.value: r.name for r in RotationType}
        return RotationType.__getattribute__(RotationType, attributes.get(string))


class BedwarsRotation:
    def __init__(
        self,
        rotation_info: dict,
        rotation_data: BedwarsStatsSnapshot
    ) -> None:
        self.uuid: str = rotation_info["uuid"]
        self.rotation: str = rotation_info["rotation"]
        self.last_reset_timestamp: float = rotation_info["last_reset_timestamp"]
        self.snapshot_id: str = rotation_info["snapshot_id"]

        self.data = rotation_data


class BedwarsHistoricalRotation:
    def __init__(
        self,
        historic_info: dict,
        historic_data: BedwarsStatsSnapshot
    ) -> None:
        self.uuid: str = historic_info["uuid"]
        self.period_id: str = historic_info["period_id"]
        self.level: int = historic_info["level"]
        self.snapshot_id: str = historic_info["snapshot_id"]

        self.data = historic_data


class HistoricalRotationPeriodID:
    def __init__(
        self,
        rotation_type: RotationType,
        datetime_info: datetime
    ) -> None:
        self.rotation_type = rotation_type
        self.datetime_info = datetime_info

    def to_string(self) -> None:
        """Format the period ID into a string"""
        format_map = {
            "daily": "daily_%Y_%m_%d",
            "weekly": "weekly_%Y_%U",
            "monthly": "monthly_%Y_%m",
            "yearly": "yearly_%Y"
        }
        return self.datetime_info.strftime(format_map[self.rotation_type.value])
