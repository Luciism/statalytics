import os
import sqlite3

from dotenv import load_dotenv

import statalib
from statalib import config
from statalib import config, REL_PATH


load_dotenv(f"{REL_PATH}/.env.test")

os.mkdir(f'{REL_PATH}/database/')
config.DB_FILE_PATH = f"{REL_PATH}/database/tests.db"
config.SHOULD_UPDATE_SUBSCRIPTION_ROLES = False
statalib.setup_database_schema(db_fp=config.DB_FILE_PATH)

class MockData:
    discord_id = 123
    discord_id_2 = 456
    uuid = "abc"


def clean_database() -> None:
    with sqlite3.connect(config.DB_FILE_PATH) as conn:
        cursor = conn.cursor()

        # Get all table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]

        # Clear each table
        for table in tables:
            cursor.execute(f"DELETE FROM {table}")


link_mock_data = lambda: statalib \
    .LinkingManager(MockData.discord_id) \
    .set_linked_data(MockData.uuid)
