from os import getenv
from dotenv import load_dotenv; load_dotenv()

from statalib import Client, setup_logging


if __name__ == '__main__':
    setup_logging()
    Client().run(getenv('BOT_TOKEN'), root_logger=True)
