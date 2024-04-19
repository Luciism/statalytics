import os
from dotenv import load_dotenv; load_dotenv()

import statalib


if __name__ == '__main__':
    statalib.setup_logging(f"{statalib.REL_PATH}/logs/bot")
    statalib.setup_database_schema()
    statalib.Client().run(os.getenv('DISCORD_BOT_TOKEN'), root_logger=True)
