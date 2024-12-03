import unittest
from datetime import datetime, UTC

from statalib.accounts import AccountVoting, voting

from utils import clean_database, MockData


class TestAddAndLoadVotes(unittest.TestCase):
    def setUp(self) -> None:
        clean_database()

    def test_add_vote(self):
        v = AccountVoting(MockData.discord_id)
        v.add_vote()

        self.assertEqual(v.load().total_votes, 1)

        v.add_vote()
        self.assertEqual(v.load().total_votes, 2)

    def test_add_vote_with_timestamp(self):
        timestamp = int(datetime.now(UTC).timestamp())

        v = AccountVoting(MockData.discord_id)
        v.add_vote(timestamp=timestamp)

        self.assertEqual(v.load().last_vote, timestamp)

    def test_add_weekend_vote(self):
        v = AccountVoting(MockData.discord_id)
        v.add_vote(is_weekend=True)

        self.assertEqual(v.load().total_votes, 1)
        self.assertEqual(v.load().weekend_votes, 1)

        v.add_vote()
        self.assertEqual(v.load().total_votes, 2)
        self.assertEqual(v.load().weekend_votes, 1)

    def test_load_empty(self):
        default = voting.VotingData(MockData.discord_id, 0, 0, None)

        v = AccountVoting(MockData.discord_id)
        self.assertEqual(v.load(), default)
