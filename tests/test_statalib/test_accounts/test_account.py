import unittest

from statalib.accounts import Account

from utils import clean_database, MockData


class TestCreateAccount(unittest.TestCase):
    def setUp(self) -> None:
        clean_database()

    def test_create_account_defaults(self):
        a = Account(MockData.discord_id)
        a.create()
        account_data = a.load(create=False)

        self.assertIsNotNone(account_data)

    def test_create_account_custom(self):
        a = Account(MockData.discord_id)
        a.create(
            creation_timestamp=1,
            permissions=["test"],
            blacklisted=True,
            account_id=1)
        account_data = a.load(create=False)

        self.assertIsNotNone(account_data)
        self.assertEqual(account_data.account_id, 1)
        self.assertEqual(account_data.creation_timestamp, 1)
        self.assertListEqual(account_data.permissions, ["test"])
        self.assertTrue(account_data.blacklisted)

    def test_create_existing_account(self):
        a = Account(MockData.discord_id)
        a.create(blacklisted=False)
        a.create(blacklisted=True)  # Does nothing.
        account_data = a.load(create=False)

        self.assertIsNotNone(account_data)
        self.assertFalse(account_data.blacklisted)


class TestLoadAccount(unittest.TestCase):
    def setUp(self) -> None:
        clean_database()

    def test_load_and_create_uncreated_account(self):
        a = Account(MockData.discord_id)
        account_data = a.load(create=True)

        self.assertIsNotNone(account_data)

    def test_load_and_dont_create_uncreated_account(self):
        a = Account(MockData.discord_id)
        account_data = a.load(create=False)

        self.assertIsNone(account_data)


class TestUpdateAccount(unittest.TestCase):
    def setUp(self) -> None:
        clean_database()

    def test_update_created_account(self):
        a = Account(MockData.discord_id)
        a.create()
        a.update(blacklisted=True, create=False)
        account_data = a.load(create=False)

        self.assertTrue(account_data.blacklisted)

    def test_update_and_create_uncreated_account(self):
        a = Account(MockData.discord_id)
        a.update(blacklisted=True, create=True)
        account_data = a.load(create=False)

        self.assertTrue(account_data.blacklisted)


class TestDeleteAccount(unittest.TestCase):
    def setUp(self) -> None:
        clean_database()

    def test_delete_created_account(self) -> None:
        a = Account(MockData.discord_id)
        a.create()
        a.delete()
        account_data = a.load(create=False)

        self.assertIsNone(account_data)

    def test_delete_uncreated_account(self) -> None:
        a = Account(MockData.discord_id)
        a.delete()
        account_data = a.load(create=False)

        self.assertIsNone(account_data)
