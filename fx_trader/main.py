import os
from utils import menu
from utils.logger import LOGGER
from utils.db import initialise_db

def setup():
    """Set up the environment for the application."""
    if os.getenv("OER_API_KEY") is None:
        LOGGER.error("No API key.", print_msg=True)
        os._exit(1)

    if not initialise_db():
        LOGGER.error("Failed to initialise database.", print_msg=True)
        os._exit(1)

def main():
    setup()
    print("Welcome to fx-trader!")
    menu.main_menu()

if __name__ == "__main__":
    main()
