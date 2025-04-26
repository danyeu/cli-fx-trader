import logging

class CustomLogger(logging.Logger):
    def debug(self, msg, *args, print_msg=False, **kwargs):
        if print_msg:
            print(msg)
        super().debug(msg, *args, **kwargs)

    def info(self, msg, *args, print_msg=False, **kwargs):
        if print_msg:
            print(msg)
        super().info(msg, *args, **kwargs)

    def warning(self, msg, *args, print_msg=False, **kwargs):
        if print_msg:
            print(msg)
        super().warning(msg, *args, **kwargs)

    def error(self, msg, *args, print_msg=False, **kwargs):
        if print_msg:
            print(msg)
        super().error(msg, *args, **kwargs)

    def exception(self, msg, *args, print_msg=False,exc_info=True, **kwargs):
        if print_msg:
            print(msg)
        super().exception(msg, *args, exc_info, **kwargs)

    def critical(self, msg, *args, print_msg=False, **kwargs):
        if print_msg:
            print(msg)
        super().critical(msg, *args, **kwargs)

LOGGER = CustomLogger(None, logging.DEBUG)
console_handler = logging.StreamHandler()
LOGGER.addHandler(console_handler)
