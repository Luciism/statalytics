import unittest
import sqlite3
from datetime import datetime, UTC

from statalib.cfg import config
from statalib.accounts.subscriptions import (
    AccountSubscriptions,
    Subscription,
    PackageTierConflictError,
)

from tests.utils import clean_database, MockData


def ts_plus(add: int | float) -> float:
    return datetime.now(UTC).timestamp() + add


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


class TestGetSubscription(unittest.TestCase):
    def setUp(self) -> None:
        clean_database()

    def test_subscription(self):
        s = AccountSubscriptions(MockData.discord_id)

        set_active_subscription("pro", now_plus(5000))
        assert s.get_subscription(False).package == "pro"

    def test_no_subscription(self):
        s = AccountSubscriptions(MockData.discord_id)

        assert s.get_subscription(False).package == "free"

    def test_subscription_expiry(self):
        s = AccountSubscriptions(MockData.discord_id)

        set_active_subscription("pro", now_plus(-1))
        assert s.get_subscription(False).package == "free"

    def test_subscription_expiry_use_paused(self):
        s = AccountSubscriptions(MockData.discord_id)

        set_active_subscription("pro", now_plus(-1))
        s._add_paused_subscription("basic", 5000)

        assert s.get_subscription(False).package == "basic"

    def test_subscription_expiry_use_highest_tier_paused(self):
        s = AccountSubscriptions(MockData.discord_id)

        set_active_subscription("pro", now_plus(-1))
        s._add_paused_subscription("pro", 5000)
        s._add_paused_subscription("basic", 5000)

        assert s.get_subscription(False).package == "pro"


class TestAddSubscription(unittest.TestCase):
    def setUp(self) -> None:
        clean_database()

    def test_add_subscription_none_existing(self):
        s = AccountSubscriptions(MockData.discord_id)

        s.add_subscription("pro", 5000, update_roles=False)

        assert s.get_subscription(False).package == "pro"

    def test_add_subscription_lower_tier_existing(self):
        s = AccountSubscriptions(MockData.discord_id)

        s.add_subscription("basic", 5000, update_roles=False)
        s.add_subscription("pro", 5000, update_roles=False)

        assert s.get_subscription(False).package == "pro"
        assert len(s._get_paused_subscriptions("basic")) == 1

    def test_add_subscription_higher_tier_existing(self):
        s = AccountSubscriptions(MockData.discord_id)

        s.add_subscription("pro", 5000, update_roles=False)
        s.add_subscription("basic", 5000, update_roles=False)

        assert s.get_subscription(False).package == "pro"
        assert len(s._get_paused_subscriptions("basic")) == 1

    def test_add_subscription_same_tier_existing_not_expired(self):
        s = AccountSubscriptions(MockData.discord_id)

        s.add_subscription("pro", 5000, update_roles=False)
        s.add_subscription("pro", 5000, update_roles=False)

        assert s.get_subscription(False).expires_in() > 5000
        assert len(s._get_paused_subscriptions("pro")) == 0


    def test_add_subscription_same_tier_existing_expired(self):
        s = AccountSubscriptions(MockData.discord_id)

        s.add_subscription("pro", -1, update_roles=False)
        s.add_subscription("pro", 5000, update_roles=False)

        assert s.get_subscription(False).expires_in() > 0
        assert len(s._get_paused_subscriptions("pro")) == 0


    def test_add_subscription_higher_tier_existing_lifetime(self):
        s = AccountSubscriptions(MockData.discord_id)

        s.add_subscription("basic", None, update_roles=False)
        s.add_subscription("pro", 5000, update_roles=False)

        sub = s.get_subscription(False)

        # Assert active subscription updated correctly
        assert sub.package == "pro"
        assert isinstance(sub.expires_in(), (float, int))

        # Permanent subscription gets paused
        assert len(s._get_paused_subscriptions("basic")) == 1


    def test_add_subscription_same_tier_existing_lifetime(self):
        s = AccountSubscriptions(MockData.discord_id)

        s.add_subscription("pro", None, update_roles=False)

        with self.assertRaisesRegex(PackageTierConflictError, ".*same tier.*"):
            s.add_subscription("pro", 5000, update_roles=False)


    def test_add_subscription_lower_tier_existing_lifetime(self):
        s = AccountSubscriptions(MockData.discord_id)

        s.add_subscription("pro", None, update_roles=False)

        with self.assertRaisesRegex(PackageTierConflictError, ".*lower tier.*"):
            s.add_subscription("basic", 5000, update_roles=False)


    def test_add_subscription_higher_tier_existing_lifetime_expiry(self):
        s = AccountSubscriptions(MockData.discord_id)

        s.add_subscription("basic", None, update_roles=False)
        s.add_subscription("pro", -1, update_roles=False)

        assert s.get_subscription(False).package == "basic"
        assert s.get_subscription(False).expiry_timestamp == None

    def test_add_subscription_lifetime_same_tier_existing(self):
        s = AccountSubscriptions(MockData.discord_id)

        s.add_subscription("pro", 5000, update_roles=False)
        s.add_subscription("pro", None, update_roles=False)

        assert s.get_subscription(False).package == "pro"
        assert s.get_subscription(False).expiry_timestamp == None
        assert len(s._get_paused_subscriptions("pro")) == 1  # Original was paused


class TestDetermineSubscriptionUpdates(unittest.TestCase):
    def setUp(self) -> None:
        clean_database()

    def test_no_subscriptions(self):
        s = AccountSubscriptions(MockData.discord_id)

        new_sub = Subscription("pro", ts_plus(3600))
        updates = s.determine_subscription_updates(new_sub)

        self.assertEqual(updates[0], new_sub)
        self.assertListEqual(updates[1], [])

    def test_active_lower_tier_subscription(self):
        s = AccountSubscriptions(MockData.discord_id)
        s.add_subscription("basic", 3600)

        new_sub = Subscription("pro", ts_plus(3600))
        updates = s.determine_subscription_updates(new_sub)

        self.assertEqual(updates[0], new_sub)
        self.assertEqual(len(updates[1]), 1)
        self.assertEqual(updates[1][0].package, "basic")

    def test_active_high_tier_subscription(self):
        s = AccountSubscriptions(MockData.discord_id)
        s.add_subscription("pro", 3600)

        new_sub = Subscription("basic", ts_plus(3600))
        updates = s.determine_subscription_updates(new_sub)

        self.assertEqual(updates[0].package, "pro")
        self.assertEqual(len(updates[1]), 1)
        self.assertEqual(updates[1][0], new_sub)

    def test_active_same_tier_subscription(self):
        """Test merging capabilities."""
        s = AccountSubscriptions(MockData.discord_id)
        s.add_subscription("pro", 3600)

        new_sub = Subscription("pro", ts_plus(3600))
        updates = s.determine_subscription_updates(new_sub)

        self.assertEqual(updates[0].package, "pro")
        self.assertGreater(updates[0].expiry_timestamp, 3600)  # Durations were added
        self.assertEqual(len(updates[1]), 0)  # No paused subscriptions

    def test_active_same_tier_subscription_add_lifetime(self):
        s = AccountSubscriptions(MockData.discord_id)
        s.add_subscription("pro", 3600)

        new_sub = Subscription("pro", None)
        updates = s.determine_subscription_updates(new_sub)

        self.assertEqual(updates[0], new_sub)
        self.assertEqual(updates[1][0].package, "pro")
        self.assertIsNotNone(updates[1][0].expiry_timestamp)
        self.assertEqual(len(updates[1]), 1)

    def test_active_same_tier_lifetime_subscription_add_non_lifetime(self):
        s = AccountSubscriptions(MockData.discord_id)
        s.add_subscription("pro", None)

        new_sub = Subscription("pro", 3600)
        with self.assertRaises(PackageTierConflictError):
            s.determine_subscription_updates(new_sub)
