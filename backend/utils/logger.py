import logging
import os
import sys

# Ensure correct module path
current_file_path = os.path.abspath(__file__)
current_dir_path = os.path.dirname(current_file_path)
parent_dir_path = os.path.dirname(current_dir_path)
sys.path.insert(0, parent_dir_path)


class Logger:
    def __init__(self, log_file_path: str):
        """Initialize logger with a specified log file."""
        self.logger = logging.getLogger(__name__)
        handler = logging.FileHandler(log_file_path, encoding="utf-8")
        handler.setLevel(logging.DEBUG)
        self.logger.setLevel(logging.DEBUG)

        # Create console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)

        # Create formatter
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

        # Add formatter
        ch.setFormatter(formatter)
        handler.setFormatter(formatter)

        # Add handlers
        self.logger.addHandler(ch)
        self.logger.addHandler(handler)

    def log(self, level: str, message: str):
        """Log a message with the specified level."""
        level = level.lower()
        if level == "debug":
            self.logger.debug(message)
        elif level == "info":
            self.logger.info(message)
        elif level == "warning":
            self.logger.warning(message)
        elif level == "error":
            self.logger.error(message)
        elif level == "critical":
            self.logger.critical(message)


# ✅ **Define `setup_logger` for Import**
def setup_logger(log_file_path="app.log"):
    """Initialize and return a logger instance."""
    return Logger(log_file_path).logger


logger = setup_logger("app.log")  # Initialize logger
