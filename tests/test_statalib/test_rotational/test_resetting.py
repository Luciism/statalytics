import unittest
from datetime import datetime, UTC

from statalib.accounts import Account
from statalib.rotational_stats import (
    has_auto_reset_access,
    RotationalStatsManager,
    RotationType,
    HistoricalRotationPeriodID,
    RotationalResetting
)

from tests.utils import clean_database, MockData, link_mock_data


mock_hypixel_data_1 = {}
mock_hypixel_data_2 = {
    "player": {"stats": {"Bedwars": {"final_kills_bedwars": 1}}}
}

auto_reset_config = {
    "whitelist_only": True,
    "uuid_whitelist": [],
    "permission_whitelist": ["automatic_tracker_reset"],
    "allow_star_permission": True
}


class TestAutoResetAccess(unittest.TestCase):
    def setUp(self) -> None:
        clean_database()

    def test_whitelist_on_uuid_not_linked(self):
        """The whitelist is on and the player is not linked."""
        assert has_auto_reset_access(MockData.uuid, auto_reset_config) is False

    def test_whitelist_off_uuid_not_linked(self):
        """The whitelist is off and the player is not linked."""
        cfg = auto_reset_config.copy()
        cfg["whitelist_only"] = False
        assert has_auto_reset_access(MockData.uuid, cfg) is True

    def test_whitelist_on_uuid_not_linked_but_whitelisted(self):
        """Player not linked to a user but the uuid is whitelisted."""
        cfg = auto_reset_config.copy()
        cfg["uuid_whitelist"] = [MockData.uuid]
        assert has_auto_reset_access(MockData.uuid, cfg) is True

    def test_whitelist_on_uuid_linked_no_perms(self):
        """The player is linked to a user but the user doesn't have auto reset perms."""
        link_mock_data()
        assert has_auto_reset_access(MockData.uuid, auto_reset_config) is False

    def test_whitelist_on_uuid_linked_has_perms(self):
        """The player is linked to a user and the user has auto reset perms."""
        link_mock_data()

        Account(MockData.discord_id).permissions \
            .add_permission("automatic_tracker_reset")

        assert has_auto_reset_access(MockData.uuid, auto_reset_config) is True


class TestRotationalResetting(unittest.TestCase):
    manager = RotationalStatsManager(MockData.uuid)

    def setUp(self) -> None:
        clean_database()

    def test_archive_rotational_data(self):
        period_id = HistoricalRotationPeriodID(RotationType.DAILY, datetime.now(UTC))

        # Initialize rotational data
        self.manager.initialize_rotational_tracking(mock_hypixel_data_1)

        # Send data to historical table
        RotationalResetting(MockData.uuid) \
            .archive_rotational_data(period_id, mock_hypixel_data_2)

        result = self.manager.get_historical_rotation_data(period_id.to_string())
        assert result.data.final_kills_bedwars == 1  # 1 Gained

    def test_refresh_rotational_data(self):
        self.manager.initialize_rotational_tracking(mock_hypixel_data_1)

        RotationalResetting(MockData.uuid) \
            .refresh_rotational_data(RotationType.DAILY, mock_hypixel_data_2)

        result = self.manager.get_rotational_data(RotationType.DAILY)
        assert result.data.final_kills_bedwars == 1  # New data
