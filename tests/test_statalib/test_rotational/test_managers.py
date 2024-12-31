from datetime import UTC, datetime
import unittest

from statalib.rotational_stats import (
    RotationalStatsManager,
    RotationType,
    HistoricalRotationPeriodID,
    RotationalResetting
)

from tests.utils import clean_database, MockData


mock_hypixel_data_1 = {}
mock_hypixel_data_2 = {
    "player": {"stats": {"Bedwars": {"final_kills_bedwars": 1}}}
}


class TestGetRotationalData(unittest.TestCase):
    manager = RotationalStatsManager(MockData.uuid)

    def setUp(self) -> None:
        clean_database()


    def test_no_data(self):
        assert self.manager.get_rotational_data(RotationType.DAILY) == None
        assert self.manager.get_rotational_data(RotationType.WEEKLY) == None
        assert self.manager.get_rotational_data(RotationType.MONTHLY) == None
        assert self.manager.get_rotational_data(RotationType.YEARLY) == None


    def test_existing_data(self):
        self.manager.initialize_rotational_tracking(mock_hypixel_data_1)

        assert self.manager.get_rotational_data(
            RotationType.DAILY).data.final_kills_bedwars == 0

        assert self.manager.get_rotational_data(
            RotationType.WEEKLY).data.final_kills_bedwars == 0

        assert self.manager.get_rotational_data(
            RotationType.MONTHLY).data.final_kills_bedwars == 0

        assert self.manager.get_rotational_data(
            RotationType.YEARLY).data.final_kills_bedwars == 0


class TestGetHistoricalRotationalData(unittest.TestCase):
    manager = RotationalStatsManager(MockData.uuid)

    def setUp(self) -> None:
        clean_database()

    def test_no_data(self):
        period_id = HistoricalRotationPeriodID(RotationType.DAILY, datetime.now(UTC))
        data = self.manager.get_historical_rotation_data(period_id.to_string())

        assert data is None

    # Test exising data in `test_resetting.TestRotationalResetting`
