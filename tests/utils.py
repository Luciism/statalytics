import os
import sqlite3

from dotenv import load_dotenv

import statalib
from statalib.accounts import Account
from statalib import config, REL_PATH


load_dotenv(f"{REL_PATH}/.env.test")

os.makedirs(f'{REL_PATH}/database/', exist_ok=True)

config.DB_FILE_PATH = f"{REL_PATH}/database/tests.db"
config.SHOULD_UPDATE_SUBSCRIPTION_ROLES = False
statalib.db.setup_database_schema(db_fp=config.DB_FILE_PATH)

class MockData:
    discord_id = 123
    discord_id_2 = 456
    uuid = "5513729a-18b1-4486-b623-db7a60a24653"
    uuid_2 = "5d9b02e2-df30-417e-9d12-0e988d5dd7a1"


def clean_database() -> None:
    with sqlite3.connect(config.DB_FILE_PATH) as conn:
        cursor = conn.cursor()

        # Get all table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]

        # Clear each table
        for table in tables:
            cursor.execute(f"DELETE FROM {table}")


link_mock_data = lambda: Account(MockData.discord_id).linking \
    .set_linked_player(MockData.uuid)
