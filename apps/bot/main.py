import os
from dotenv import load_dotenv; load_dotenv()

import statalib
from helper import Client


if __name__ == '__main__':
    statalib.loggers.setup_logging(f"{statalib.REL_PATH}/logs/bot")
    statalib.setup_database_schema()
    Client().run(os.getenv('DISCORD_BOT_TOKEN'), root_logger=True)
