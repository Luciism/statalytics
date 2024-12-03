"""Account voting related functionality."""

from dataclasses import dataclass
from datetime import datetime, UTC

from ..functions import db_connect


@dataclass
class VotingData:
    """Voting related data."""
    discord_id: int
    "The Discord user ID of the user."
    total_votes: int
    "The total number of votes."
    weekend_votes: int
    "The total number of votes during the weekend."
    last_vote: float | None
    "The timestamp of the last vote."

    @property
    def formatted_last_vote_date(self) -> str | None:
        """The formatted date of the last vote (%d/%m/%Y)."""
        if self.last_vote is None:
            return None

        last_vote_dt = datetime.fromtimestamp(self.last_vote, UTC)
        return last_vote_dt.strftime('%d/%m/%Y')


class AccountVoting:
    """A voting manager for the account."""
    def __init__(self, discord_user_id: int) -> None:
        self._discord_user_id = discord_user_id

    def load(self) -> VotingData:
        """Load the account's voting data from the database."""
        with db_connect() as conn:
            cursor = conn.cursor()

            voting_data = cursor.execute(
                f'SELECT * FROM voting_data WHERE discord_id = ?', (self._discord_user_id,)
            ).fetchone()

        return VotingData(*(voting_data or (self._discord_user_id, 0, 0, None)))

    def add_vote(
        self,
        is_weekend: bool=False,
        timestamp: float | None=None
    ) -> None:
        """
        Add a vote to the account's voting data.

        :param is_weekend: Whether the process was processed during the weekend.
        :param timestamp: Optionally, the timestamp of when the vote was cast.
        """
        if timestamp is None:
            timestamp = datetime.now(UTC).timestamp()

        with db_connect() as conn:
            cursor = conn.cursor()

            current_voting_data = cursor.execute(
                f'SELECT * FROM voting_data WHERE discord_id = ?', (self._discord_user_id,)
            ).fetchone()

            if current_voting_data:
                cursor.execute(f"""
                    UPDATE voting_data
                    SET
                        total_votes = total_votes + 1,
                        {'weekend_votes = weekend_votes + 1,' if is_weekend else ''}
                        last_vote = ?
                    WHERE discord_id = ?
                """, (timestamp, self._discord_user_id,))
            else:
                cursor.execute(
                    'INSERT INTO voting_data (discord_id, total_votes, '
                    'weekend_votes, last_vote) VALUES (?, ?, ?, ?)',
                    (self._discord_user_id, 1, int(is_weekend), timestamp))
