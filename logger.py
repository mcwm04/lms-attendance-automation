"""
=========================================================
Application Logger
LMS Attendance Automation System
Version 8
=========================================================
"""

import logging
from datetime import datetime

from path_manager import PathManager


class AppLogger:

    _logger = None

    @classmethod
    def get_logger(cls):

        if cls._logger:
            return cls._logger

        log_file = PathManager.LOGS_DIR / f"{datetime.now():%Y-%m-%d}.log"

        logger = logging.getLogger("LMSAutomation")

        logger.setLevel(logging.INFO)

        logger.propagate = False

        if logger.handlers:
            logger.handlers.clear()

        formatter = logging.Formatter(
            "[%(asctime)s] %(levelname)s : %(message)s",
            "%H:%M:%S"
        )
        PathManager.LOGS_DIR.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(
            log_file,
            encoding="utf-8"
        )
        file_handler.setFormatter(formatter)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

        cls._logger = logger

        return logger