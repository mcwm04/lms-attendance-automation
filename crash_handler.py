"""
=========================================================
Global Crash Handler
LMS Attendance Automation System
Version 8
=========================================================
"""

import sys
import traceback
from datetime import datetime

from logger import AppLogger
from path_manager import PathManager

log = AppLogger.get_logger()


def handle_exception(exc_type, exc_value, exc_traceback):
    """
    Global unhandled exception handler.
    """

    # Ignore Ctrl+C
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    try:

        PathManager.CRASH_DIR.mkdir(parents=True, exist_ok=True)

        crash_file = (
            PathManager.CRASH_DIR /
            f"Crash_{datetime.now():%Y-%m-%d_%H-%M-%S}.log"
        )

        with open(crash_file, "w", encoding="utf-8") as f:
            traceback.print_exception(
                exc_type,
                exc_value,
                exc_traceback,
                file=f
            )

        log.error(
            f"Application crashed. Crash report saved to {crash_file}"
        )

    except Exception:

        # Last resort: avoid crashing the crash handler itself.
        pass


def install():
    """
    Install the global exception handler.
    """
    sys.excepthook = handle_exception