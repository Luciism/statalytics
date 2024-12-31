import unittest

from statalib import config
from statalib.rotational_stats import get_max_lookback

from statalib.accounts.subscriptions import AccountSubscriptions
from tests.utils import clean_database, MockData


# Ensure subscription config is expected
def set_package_max_lookback(package: str, lookback: int | None):
    config._config_data["global"]["subscriptions"]["packages"] \
        .setdefault(package, {}) \
        .setdefault("properties", {})["max_lookback"] = lookback

def setup_config():
    config._load_config_data()
    config._config_data \
        .setdefault("global", {}) \
        .setdefault("subscription", {}) \
        .setdefault("packages, {}")

    set_package_max_lookback("free", 30)
    set_package_max_lookback("basic", 60)
    set_package_max_lookback("pro", None)


class TestGetMaxLookback(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        setup_config()

    @classmethod
    def tearDownClass(cls) -> None:
        config.refresh()

    def setUp(self) -> None:
        clean_database()

    def test_no_subscription(self):
        max_lookback = get_max_lookback([MockData.discord_id, MockData.discord_id_2])
        assert max_lookback == 30

    def test_primary_has_extended(self):
        AccountSubscriptions(MockData.discord_id).add_subscription("basic", update_roles=False)

        max_lookback = get_max_lookback([MockData.discord_id, MockData.discord_id_2])
        assert max_lookback == 60

    def test_secondary_has_extended(self):
        AccountSubscriptions(MockData.discord_id_2).add_subscription("basic")

        max_lookback = get_max_lookback([MockData.discord_id, MockData.discord_id_2])
        assert max_lookback == 60

    def test_primary_has_permanent(self):
        AccountSubscriptions(MockData.discord_id).add_subscription("pro")

        max_lookback = get_max_lookback([MockData.discord_id, MockData.discord_id_2])
        assert max_lookback is None


    def test_secondary_has_permanent(self):
        AccountSubscriptions(MockData.discord_id_2).add_subscription("pro")

        max_lookback = get_max_lookback([MockData.discord_id, MockData.discord_id_2])
        assert max_lookback is None


    def test_no_users(self):
        max_lookback = get_max_lookback([])
        assert max_lookback == 30
