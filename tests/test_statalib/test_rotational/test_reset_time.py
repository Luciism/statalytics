import unittest

from statalib.rotational_stats import (
    ConfiguredResetTimeManager,
    DefaultResetTimeManager,
    ResetTime,
    get_dynamic_reset_time
)
from utils import MockData, clean_database, link_mock_data


class BaseTestResetTime:
    manager: DefaultResetTimeManager | ConfiguredResetTimeManager

    def setUp(self) -> None:
        clean_database()

    def test_update_reset_time_no_existing(self):
        self.manager.update(ResetTime())
        reset_time = self.manager.get()

        assert reset_time.utc_offset == 0
        assert reset_time.reset_hour in range(0, 23)

    def test_update_reset_time_override(self):
        self.manager.update(ResetTime())  # Initial value
        self.manager.update(ResetTime(1, 2))  # Final value

        assert self.manager.get() == ResetTime(1, 2)

    def test_update_reset_time_one_value(self):
        self.manager.update(ResetTime(2, 0))  # Initial
        self.manager.update(ResetTime(reset_hour=4))  # Final

        assert self.manager.get() == ResetTime(2, 4)

    def test_get_reset_time_no_existing(self):
        assert self.manager.get() == None

    def test_unset_reset_time_value(self):
        self.manager.update(ResetTime())
        self.manager.remove()

        assert self.manager.get() == None


class TestDefaultResetTime(BaseTestResetTime, unittest.TestCase):
    manager = DefaultResetTimeManager(MockData.uuid)


class TestConfiguredResetTime(BaseTestResetTime, unittest.TestCase):
    manager = ConfiguredResetTimeManager(MockData.discord_id)


class TestGetDynamicResetTime(unittest.TestCase):
    manager_default = DefaultResetTimeManager(MockData.uuid)
    manager_configured = ConfiguredResetTimeManager(MockData.discord_id)

    def setUp(self) -> None:
        clean_database()

    def test_default_but_no_configured(self):
        """A default reset time is set but not a configured reset time"""
        # Link account
        link_mock_data()

        self.manager_default.update(ResetTime(0, 0))
        reset_time = get_dynamic_reset_time(MockData.uuid)

        assert reset_time == ResetTime(0, 0)

    def test_configured_but_no_default(self):
        """A configured reset time is set but not a default reset time"""
        # Link account
        link_mock_data()

        self.manager_configured.update(ResetTime(0, 0))
        reset_time = get_dynamic_reset_time(MockData.uuid)

        assert reset_time == ResetTime(0, 0)


    def test_configured_and_default(self):
        """A configured reset time is set but not a default reset time"""
        # Link account
        link_mock_data()

        self.manager_default.update(ResetTime(0, 0))
        self.manager_configured.update(ResetTime(1, 1))

        reset_time = get_dynamic_reset_time(MockData.uuid)
        assert reset_time == ResetTime(1, 1)  # Should use configured


    def test_neither_configured_nor_default(self):
        """Neither a configured reset time nor a default reset time is set."""
        # Link account
        link_mock_data()

        reset_time = get_dynamic_reset_time(MockData.uuid)
        assert reset_time == ResetTime(0, 0)
