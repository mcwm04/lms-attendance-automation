"""
=========================================================
Build Information
LMS Attendance Automation System
Version 8.1
=========================================================

CHANGE NOTE (2026-08-15):
    APP_VERSION bumped from "8.0.0" to "8.1.0" to match the
    actual on-disk project version ("LMS Automation Version 8.1")
    and the installer's AppVersion (setup.iss). This value drives
    app_info.py's VERSION / FULL_VERSION / WINDOW_TITLE and
    version_info.py's FILE_VERSION / PRODUCT_VERSION used in the
    PyInstaller Windows version resource — previously it was
    stuck one minor version behind everywhere it's displayed.
=========================================================
"""

APP_NAME = "LMS Attendance Automation System"

APP_VERSION = "8.1.0"

BUILD_NUMBER = "001"

COMPANY = "Waqas Ahmad"

COPYRIGHT = "© 2026 Waqas Ahmad"

WEBSITE = ""

BUILD_MODE = "Development"
