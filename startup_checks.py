"""
=========================================================
Startup Diagnostics
LMS Attendance Automation System
Version 8
=========================================================
"""
import shutil
from logger import AppLogger
from config.config_manager import ConfigManager
from path_manager import PathManager


log = AppLogger.get_logger()


def run_startup_checks():

    log.info("Running startup diagnostics...")

    # --------------------------------------------------
    # Check configuration
    # --------------------------------------------------

    try:

        config_file = PathManager.config("defaults.json")

        if not config_file.exists():
            raise FileNotFoundError(
                f"Configuration file not found: {config_file}"
            )

        ConfigManager.load()

        log.info("✓ Configuration loaded")

    except Exception as e:

        log.error(f"Configuration error: {e}")

        raise

    # --------------------------------------------------
    # Check log directory
    # --------------------------------------------------

    PathManager.LOGS_DIR.mkdir(parents=True, exist_ok=True)

    if PathManager.LOGS_DIR.is_dir():
        log.info("✓ Log directory available")
    else:
        raise RuntimeError("Unable to access log directory")

    # --------------------------------------------------
    # Check temp directory
    # --------------------------------------------------

    PathManager.TEMP_DIR.mkdir(parents=True, exist_ok=True)

    if PathManager.TEMP_DIR.is_dir():
        log.info("✓ Temp directory available")
    else:
        raise RuntimeError("Unable to access temp directory")

    # --------------------------------------------------
    # Check crash directory
    # --------------------------------------------------

    PathManager.CRASH_DIR.mkdir(parents=True, exist_ok=True)

    if PathManager.CRASH_DIR.is_dir():
        log.info("✓ Crash directory available")
    else:
        raise RuntimeError("Unable to access crash directory")

    log.info("Startup diagnostics completed successfully.")