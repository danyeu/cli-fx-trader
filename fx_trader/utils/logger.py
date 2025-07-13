import logging

def setup_logging(level=logging.DEBUG) -> None:
    """Sets up logging for the application."""
    logging.basicConfig(
        level=level,
        format='%(asctime)s | %(levelname)s | %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            logging.StreamHandler()  # Output to console
        ]
    )
