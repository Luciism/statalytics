import sqlite3
import unittest

from statalib import sessions

import statalib
from utils import clean_database, MockData


mock_hypixel_data_1 = {}
mock_hypixel_data_2 = {
    "player": {"stats": {"Bedwars": {"final_kills_bedwars": 1}}}
}


class TestCreateAndGetSession(unittest.TestCase):
    manager = sessions.SessionManager(MockData.uuid)

    def setUp(self) -> None:
        clean_database()

    def test_create_session_none_existing(self):
        self.manager.create_session(1, hypixel_data=mock_hypixel_data_1)

        self.assertIsNotNone(self.manager.get_session(1))

    def test_create_session_already_exists(self):
        self.manager.create_session(1, mock_hypixel_data_1)

        with self.assertRaises(sqlite3.IntegrityError):
            self.manager.create_session(1, mock_hypixel_data_1)

    def get_session_doesnt_exist(self):
        self.assertIsNone(self.manager.get_session(1))


class TestDeleteSessions(unittest.TestCase):
    manager = sessions.SessionManager(MockData.uuid)

    def setUp(self) -> None:
        clean_database()

    def test_delete_existing_session(self):
        self.manager.create_session(1, mock_hypixel_data_1)
        self.manager.delete_session(1)

        self.assertIsNone(self.manager.get_session(1))

    def test_delete_non_existing_session(self):
        with self.assertRaisesRegex(
            statalib.DataNotFoundError, "not found for player"
        ):
            self.manager.delete_session(1)


class TestListSessions(unittest.TestCase):
    manager = sessions.SessionManager(MockData.uuid)

    def setUp(self) -> None:
        clean_database()

    def test_list_sessions_none_exist(self):
        self.assertListEqual(self.manager.active_sessions(), [])

    def test_list_sessions(self):
        self.manager.create_session(1, mock_hypixel_data_1)
        self.assertListEqual(self.manager.active_sessions(), [1])

    def test_list_sessions_order_ascending(self):
        self.manager.create_session(2, mock_hypixel_data_1)
        self.manager.create_session(1, mock_hypixel_data_1)

        self.assertListEqual(self.manager.active_sessions(), [1, 2])

    def test_session_count(self):
        self.manager.create_session(1, mock_hypixel_data_1)
        self.manager.create_session(2, mock_hypixel_data_1)
        self.assertEqual(self.manager.session_count(), 2)

    def test_session_count_no_sessions(self):
        self.assertEqual(self.manager.session_count(), 0)