import unittest
import sqlite3
from datetime import datetime, UTC

from statalib.cfg import config
from statalib.common import REL_PATH
from statalib.subscriptions import (
    SubscriptionManager,
    PackageTierConflictError
)


config.DB_FILE_PATH = f"{REL_PATH}/database/tests.db"


class MockData:
    discord_id = 123


def set_active_subscription(
    package: str,
    expires: int,
    discord_id: int = None
) -> None:
    discord_id = discord_id or MockData.discord_id

    with sqlite3.connect(config.DB_FILE_PATH) as conn:
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM subscriptions_active WHERE discord_id = ?", (discord_id,))

        if cursor.fetchone():
            cursor.execute(
                "UPDATE subscriptions_active SET package = ?, expires = ? "
                "WHERE discord_id = ?", (package, expires, discord_id)
            )
        else:
            cursor.execute(
                "INSERT INTO subscriptions_active (discord_id, package, expires) "
                "VALUES (?, ?, ?)", (discord_id, package, expires)
            )


def now_plus(x: int) -> int:
    return int(datetime.now(UTC).timestamp() + x)


def clean_database() -> None:
    with sqlite3.connect(config.DB_FILE_PATH) as conn:
        cursor = conn.cursor()

        # Get all table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]

        # Clear each table
        for table in tables:
            cursor.execute(f"DELETE FROM {table}")


class TestGetSubscription(unittest.TestCase):
    def setUp(self) -> None:
        clean_database()

    def test_subscription(self):
        s = SubscriptionManager(MockData.discord_id)

        set_active_subscription("pro", now_plus(5000))
        assert s.get_subscription(False).package == "pro"

    def test_no_subscription(self):
        s = SubscriptionManager(MockData.discord_id)

        assert s.get_subscription(False).package == "free"

    def test_subscription_expiry(self):
        s = SubscriptionManager(MockData.discord_id)

        set_active_subscription("pro", now_plus(-1))
        assert s.get_subscription(False).package == "free"

    def test_subscription_expiry_use_paused(self):
        s = SubscriptionManager(MockData.discord_id)

        set_active_subscription("pro", now_plus(-1))
        s._add_paused_subscription("basic", 5000)

        assert s.get_subscription(False).package == "basic"

    def test_subscription_expiry_use_highest_tier_paused(self):
        s = SubscriptionManager(MockData.discord_id)

        set_active_subscription("pro", now_plus(-1))
        s._add_paused_subscription("pro", 5000)
        s._add_paused_subscription("basic", 5000)

        assert s.get_subscription(False).package == "pro"


class TestAddSubscription(unittest.TestCase):
    def setUp(self) -> None:
        clean_database()

    def test_add_subscription_none_existing(self):
        s = SubscriptionManager(MockData.discord_id)

        s.add_subscription("pro", 5000)

        assert s.get_subscription(False).package == "pro"

    def test_add_subscription_lower_tier_existing(self):
        s = SubscriptionManager(MockData.discord_id)

        s.add_subscription("basic", 5000)
        s.add_subscription("pro", 5000)

        assert s.get_subscription(False).package == "pro"
        assert len(s._get_paused_subscriptions("basic")) == 1

    def test_add_subscription_higher_tier_existing(self):
        s = SubscriptionManager(MockData.discord_id)

        s.add_subscription("pro", 5000)
        s.add_subscription("basic", 5000)

        assert s.get_subscription(False).package == "pro"
        assert len(s._get_paused_subscriptions("basic")) == 1

    def test_add_subscription_same_tier_existing_not_expired(self):
        s = SubscriptionManager(MockData.discord_id)

        s.add_subscription("pro", 5000)
        s.add_subscription("pro", 5000)

        assert s.get_subscription(False).expires_in() > 5000
        assert len(s._get_paused_subscriptions("pro")) == 0


    def test_add_subscription_same_tier_existing_expired(self):
        s = SubscriptionManager(MockData.discord_id)

        s.add_subscription("pro", -1)
        s.add_subscription("pro", 5000)

        assert s.get_subscription(False).expires_in() > 0
        assert len(s._get_paused_subscriptions("pro")) == 0


    def test_add_subscription_higher_tier_existing_lifetime(self):
        s = SubscriptionManager(MockData.discord_id)

        s.add_subscription("basic", None)
        s.add_subscription("pro", 5000)

        sub = s.get_subscription(False)

        # Assert active subscription updated correctly
        assert sub.package == "pro"
        assert isinstance(sub.expires_in(), (float, int))

        # Permanent subscription gets paused
        assert len(s._get_paused_subscriptions("basic")) == 1


    def test_add_subscription_same_tier_existing_lifetime(self):
        s = SubscriptionManager(MockData.discord_id)

        s.add_subscription("pro", None)

        with self.assertRaisesRegex(PackageTierConflictError, ".*same tier.*"):
            s.add_subscription("pro", 5000)


    def test_add_subscription_lower_tier_existing_lifetime(self):
        s = SubscriptionManager(MockData.discord_id)

        s.add_subscription("pro", None)

        with self.assertRaisesRegex(PackageTierConflictError, ".*lower tier.*"):
            s.add_subscription("basic", 5000)


    def test_add_subscription_higher_tier_existing_lifetime_expiry(self):
        s = SubscriptionManager(MockData.discord_id)

        s.add_subscription("basic", None)
        s.add_subscription("pro", -1)

        assert s.get_subscription(False).package == "basic"
        assert s.get_subscription(False).expiry_timestamp == None
