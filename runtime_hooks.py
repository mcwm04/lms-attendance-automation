"""
=========================================================
PyInstaller Runtime Hook
LMS Attendance Automation System
Version 8
=========================================================
"""

# ==========================================================
# UTF-8 Console / PyInstaller Compatibility
# ==========================================================

import os
import sys

os.environ.setdefault("PYTHONIOENCODING", "utf-8")


class DummyStream:
    """Fallback stream for windowed PyInstaller builds."""

    def write(self, text):
        pass

    def flush(self):
        pass

    def isatty(self):
        return False


# ----------------------------------------------------------
# stdout
# ----------------------------------------------------------

if sys.stdout is None:
    sys.stdout = DummyStream()

elif hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(
        encoding="utf-8",
        errors="replace"
    )

# ----------------------------------------------------------
# stderr
# ----------------------------------------------------------

if sys.stderr is None:
    sys.stderr = DummyStream()

elif hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(
        encoding="utf-8",
        errors="replace"
    )


def initialize():
    """
    Runtime initialization for frozen applications.
    """

    if getattr(sys, "frozen", False):
        os.environ.setdefault("PYTHONUTF8", "1")
        os.environ.setdefault("PYTHONIOENCODING", "utf-8")


initialize()