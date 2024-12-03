import unittest

from statalib.accounts import AccountLinking, linking

from utils import clean_database, MockData


class TestGetAndSetLinkedPlayer(unittest.TestCase):
    def setUp(self) -> None:
        clean_database()

    def test_linking_unique_insert(self):
        l = AccountLinking(MockData.discord_id)
        l.set_linked_player(MockData.uuid)

        self.assertEqual(l.get_linked_player_uuid(), MockData.uuid)

    def test_linking_override_update(self):
        l = AccountLinking(MockData.discord_id)
        l.set_linked_player(MockData.uuid)  # Set initial linked player
        l.set_linked_player(MockData.uuid_2)  # Override linked player

        self.assertEqual(l.get_linked_player_uuid(), MockData.uuid_2)

    def test_linking_duplicates(self):
        l1 = AccountLinking(MockData.discord_id)
        l2 = AccountLinking(MockData.discord_id_2)

        l1.set_linked_player(MockData.uuid)  # Set linked player
        l2.set_linked_player(MockData.uuid)  # Set same linked player

        # Should allow multiple linking
        self.assertEqual(l1.get_linked_player_uuid(), MockData.uuid)
        self.assertEqual(l2.get_linked_player_uuid(), MockData.uuid)

    def test_get_non_linked(self):
        l = AccountLinking(MockData.discord_id)

        self.assertIsNone(l.get_linked_player_uuid())


class TestUnlinkAccount(unittest.TestCase):
    def setUp(self) -> None:
        clean_database()

    def test_unlink_account(self):
        l = AccountLinking(MockData.discord_id)
        l.set_linked_player(MockData.uuid)  # Set initial linked player
        l.unlink_account()

        self.assertIsNone(l.get_linked_player_uuid())

    def test_unlink_non_linked(self):
        l = AccountLinking(MockData.discord_id)
        l.unlink_account()

        self.assertIsNone(l.get_linked_player_uuid())


class TestUtilityFunctions(unittest.TestCase):
    def setUp(self) -> None:
        clean_database()

    def test_get_total_linked_accounts_no_accounts(self):
        self.assertEqual(linking.get_total_linked_accounts(), 0)

    def test_get_total_linked_accounts(self):
        l = AccountLinking(MockData.discord_id)
        l.set_linked_player(MockData.uuid)

        self.assertEqual(linking.get_total_linked_accounts(), 1)

    def test_get_total_linked_accounts_unlinked(self):
        l = AccountLinking(MockData.discord_id)
        l.set_linked_player(MockData.uuid)
        l.unlink_account()

        self.assertEqual(linking.get_total_linked_accounts(), 0)

    def test_uuid_to_discord_id_no_account(self):
        self.assertIsNone(linking.uuid_to_discord_id(MockData.uuid))

    def test_uuid_to_discord_id(self):
        l = AccountLinking(MockData.discord_id)
        l.set_linked_player(MockData.uuid)

        self.assertEqual(
            linking.uuid_to_discord_id(MockData.uuid), MockData.discord_id)

    def test_uuid_to_discord_id_duplicates(self):
        l1 = AccountLinking(MockData.discord_id)
        l1.set_linked_player(MockData.uuid)

        l2 = AccountLinking(MockData.discord_id_2)
        l2.set_linked_player(MockData.uuid)

        # Should use first entry.
        self.assertEqual(
            linking.uuid_to_discord_id(MockData.uuid), MockData.discord_id)



# TODO: test autofill
