"""
=========================================================
Application Bootstrap
LMS Attendance Automation System
Version 8
=========================================================
"""

from path_manager import PathManager
from crash_handler import install
from startup_checks import run_startup_checks
import shutil
from logger import AppLogger
from version_info import APP_NAME

log = AppLogger.get_logger()

class Bootstrap:
    """
    Central application bootstrap.

    Responsible for:
    - Creating required application folders
    - Installing the global crash handler
    - Running startup diagnostics
    """

    @staticmethod
    def _initialize_configuration():
        """Initialize application configuration."""

        # Ensure folders exist
        PathManager.USER_DATA_DIR.mkdir(parents=True, exist_ok=True)

        default_config = PathManager.config("defaults.json")
        user_config = PathManager.user_config()

        # Verify bundled configuration exists
        if not default_config.exists():
            raise FileNotFoundError(
                f"Bundled configuration missing: {default_config}"
            )

        # First run → create user configuration
        if not user_config.exists():
            shutil.copy2(default_config, user_config)

    @staticmethod    
    def initialize():
        log.info("=" * 60)
        log.info(f"Starting {APP_NAME}")
        log.info("Initializing application...")
        log.info("=" * 60)
        """Initialize the application infrastructure."""

        # -----------------------------------------------------
        # Create required folders
        # -----------------------------------------------------

        folders = [
            PathManager.LOGS_DIR,
            PathManager.CACHE_DIR,
            PathManager.CRASH_DIR,
            PathManager.TEMP_DIR,
        ]

        for folder in folders:
            folder.mkdir(parents=True, exist_ok=True)

        # -----------------------------------------------------
        # Initialize configuration
        # -----------------------------------------------------
        Bootstrap._initialize_configuration()

        # -----------------------------------------------------
        # Install global crash handler
        # -----------------------------------------------------

        install()

        # -----------------------------------------------------
        # Run startup diagnostics
        # -----------------------------------------------------

        run_startup_checks()