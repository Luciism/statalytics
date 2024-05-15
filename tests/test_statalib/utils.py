import sqlite3

from dotenv import load_dotenv

from statalib import config, REL_PATH


load_dotenv(f"{REL_PATH}/.env.test")

config.DB_FILE_PATH = f"{REL_PATH}/database/tests.db"


class MockData:
    discord_id = 123


def clean_database() -> None:
    with sqlite3.connect(config.DB_FILE_PATH) as conn:
        cursor = conn.cursor()

        # Get all table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]

        # Clear each table
        for table in tables:
            cursor.execute(f"DELETE FROM {table}")
