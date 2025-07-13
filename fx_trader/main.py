from logging import getLogger
import os
from utils import menu
from utils.logger import setup_logging
from utils.db import initialise_db

setup_logging()
logger = getLogger(__name__)

def setup():
    """Set up the environment for the application."""
    def print_log_exit(message: str):
        print(message)
        logger.error(message)
        os._exit(1)

    if os.getenv("OER_API_KEY") is None:
        print_log_exit("No API key.")

    if not initialise_db():
        print_log_exit("Failed to initialise database.")

def main():
    setup()
    print("Welcome to fx-trader!")
    menu.main_menu()

if __name__ == "__main__":
    main()
