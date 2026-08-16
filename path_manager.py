"""
=========================================================
Path Manager
LMS Attendance Automation System
Version 8
=========================================================
"""

from pathlib import Path
import sys


class PathManager:
    """
    Centralized application path manager.

    Automatically detects:
    - Development mode
    - PyInstaller one-file
    - PyInstaller one-folder
    """

    IS_FROZEN = getattr(sys, "frozen", False)

    if IS_FROZEN:
        # Running as PyInstaller executable
        ROOT_DIR = Path(sys.executable).resolve().parent
        RESOURCE_DIR = Path(getattr(sys, "_MEIPASS"))
    else:
        # Running from source
        ROOT_DIR = Path(__file__).resolve().parent
        RESOURCE_DIR = ROOT_DIR

    # ---------------------------------------------------------
    # Application folders
    # ---------------------------------------------------------

    ASSETS_DIR = RESOURCE_DIR / "assets"
    CONFIG_DIR = RESOURCE_DIR / "config"
    USER_DATA_DIR = ROOT_DIR / "UserData"
    LOGS_DIR = ROOT_DIR / "Logs"
    CACHE_DIR = ROOT_DIR / "Cache"
    CRASH_DIR = ROOT_DIR / "Crash"
    TEMP_DIR = ROOT_DIR / "Temp"

    # ---------------------------------------------------------
    # Convenience methods
    # ---------------------------------------------------------

    @classmethod
    def user_data(cls, *parts):
        return cls.USER_DATA_DIR.joinpath(*parts)

    @classmethod
    def user_config(cls):
        return cls.user_data("config.json")

    @classmethod
    def default_config(cls):
        """Return the bundled default configuration file."""
        return cls.config("defaults.json")

    @classmethod
    def asset(cls, *parts):
        """Return a path inside the assets directory."""
        return cls.ASSETS_DIR.joinpath(*parts)

    @classmethod
    def config(cls, *parts):
        """Return a path inside the config directory."""
        return cls.CONFIG_DIR.joinpath(*parts)

    @classmethod
    def logs(cls, *parts):
        """Return a path inside the logs directory."""
        return cls.LOGS_DIR.joinpath(*parts)

    @classmethod
    def cache(cls, *parts):
        """Return a path inside the cache directory."""
        return cls.CACHE_DIR.joinpath(*parts)

    @classmethod
    def crash(cls, *parts):
        """Return a path inside the crash directory."""
        return cls.CRASH_DIR.joinpath(*parts)

    @classmethod
    def temp(cls, *parts):
        """Return a path inside the temp directory."""
        return cls.TEMP_DIR.joinpath(*parts)
    # -----------------------------------------------------
# Course Settings
# -----------------------------------------------------

    COURSES_DIR = USER_DATA_DIR / "courses"


    @classmethod
    def course_settings(cls, filename: str):
        """
        Returns the full path of a course settings file.

        Example:
            Database Systems.json
        """
        return cls.COURSES_DIR / filename