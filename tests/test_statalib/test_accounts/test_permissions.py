import unittest

from statalib import config
from statalib.accounts import AccountPermissions, Account

from tests.utils import clean_database, MockData

def setup_config():
    config._load_config_data()
    config._config_data \
        .setdefault("global", {}) \
        .setdefault("subscription", {}) \
        .setdefault("packages, {}")

    config._config_data["global"]["subscriptions"]["packages"]["test"] = {
        "tier": 3,
        "role_id": 0,
        "permissions": ["test", "test2"],
        "properties": {
            "max_sessions": 5,
            "max_lookback": None,
            "generic_command_cooldown": {
                "rate": 1,
                "per": 0
            }
        }
    }

class TestCaseBase(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        setup_config()

    @classmethod
    def tearDownClass(cls) -> None:
        config.refresh()

    def setUp(self) -> None:
        clean_database()

class TestAddPermissions(TestCaseBase):
    def test_add_permission(self):
        p = AccountPermissions(MockData.discord_id)
        p.add_permission("test")

        self.assertIn("test", p.get_permissions())

    def test_add_duplicate_permission(self):
        p = AccountPermissions(MockData.discord_id)
        p.add_permission("test")
        p.add_permission("test")

        self.assertIn("test", p.get_permissions())
        self.assertEqual(len(p.get_permissions()), 1)

    def test_add_empty_string_permission(self):
        p = AccountPermissions(MockData.discord_id)
        p.add_permission("")

        self.assertEqual(len(p.get_permissions()), 0)

class TestAddPermissionsCreatedAccount(TestAddPermissions):
    def setUp(self) -> None:
        super().setUp()
        Account(MockData.discord_id).create()


class TestSetPermissions(TestCaseBase):
    def test_set_permissions(self):
        p = AccountPermissions(MockData.discord_id)
        p.set_permissions(["test"])

        self.assertIn("test", p.get_permissions())
        self.assertEqual(len(p.get_permissions()), 1)

    def test_set_empty_permissions(self):
        p = AccountPermissions(MockData.discord_id)
        p.add_permission("test")
        p.set_permissions([])

        self.assertEqual(len(p.get_permissions()), 0)

    def test_set_duplicate_permissions(self):
        p = AccountPermissions(MockData.discord_id)
        p.set_permissions(["test", "test"])

        self.assertIn("test", p.get_permissions())
        self.assertEqual(len(p.get_permissions()), 1)

    def test_set_empty_string_permission(self):
        p = AccountPermissions(MockData.discord_id)
        p.set_permissions([""])

        self.assertEqual(len(p.get_permissions()), 0)

class TestSetPermissionsCreatedAccount(TestSetPermissions):
    def setUp(self) -> None:
        super().setUp()
        Account(MockData.discord_id).create()


class TestGetPermissions(TestCaseBase):
    def test_get_permissions_no_permissions(self):
        p = AccountPermissions(MockData.discord_id)

        self.assertEqual(len(p.get_permissions()), 0)

class TestGetPermissionsCreatedAccount(TestGetPermissions):
    def setUp(self) -> None:
        super().setUp()
        Account(MockData.discord_id).create()


class TestRemovePermission(TestCaseBase):
    def remove_permission(self):
        p = AccountPermissions(MockData.discord_id)
        p.add_permission("test")
        p.remove_permission("test")

        self.assertEqual(len(p.get_permissions()), 0)

    def remove_non_existent_permission(self):
        p = AccountPermissions(MockData.discord_id)
        p.remove_permission("test")

        self.assertEqual(len(p.get_permissions()), 0)

class TestRemovePermissionCreatedAccount(TestRemovePermission):
    def setUp(self) -> None:
        super().setUp()
        Account(MockData.discord_id).create()


class TestHasPermission(TestCaseBase):
    def test_has_permission_no_permissions(self):
        p = AccountPermissions(MockData.discord_id)

        self.assertFalse(p.has_permission("test"))

    def test_has_permission(self):
        p = AccountPermissions(MockData.discord_id)
        p.add_permission("test")

        self.assertTrue(p.has_permission("test"))

    def test_has_one_of_permissions(self):
        p = AccountPermissions(MockData.discord_id)
        p.add_permission("test")

        # Has one or more of the following
        self.assertTrue(p.has_permission(["test", "test2"]))

    def has_permission_with_star(self):
        p = AccountPermissions(MockData.discord_id)
        p.add_permission("*")

        self.assertTrue(p.has_permission(["test"], allow_star=True))

class TestHasPermissionCreatedAccount(TestHasPermission):
    def setUp(self) -> None:
        super().setUp()
        Account(MockData.discord_id).create()



class TestHasAccess(TestCaseBase):
    def _add_test_subscription(self):
        Account(MockData.discord_id).subscriptions.add_subscription("test")

    def test_has_access_no_subscription(self):
        p = AccountPermissions(MockData.discord_id)

        self.assertFalse(p.has_access("test"))

    def test_has_access_permission_no_subscription(self):
        p = AccountPermissions(MockData.discord_id)
        p.add_permission("test")

        self.assertTrue(p.has_access("test"))

    def test_has_access_subscription(self):
        p = AccountPermissions(MockData.discord_id)
        self._add_test_subscription()

        self.assertTrue(p.has_access("test"))

    def test_has_access_subscription_star_permission(self):
        p = AccountPermissions(MockData.discord_id)
        self._add_test_subscription()
        p.add_permission("*")

        self.assertTrue(p.has_access("idk", allow_star=True))

class TestHasAccessCreatedAccount(TestHasAccess):
    def setUp(self) -> None:
        super().setUp()
        Account(MockData.discord_id).create()
