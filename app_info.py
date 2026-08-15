"""
=========================================================
Application Information
LMS Attendance Automation System
Version 8
=========================================================
"""

from build_info import (
    APP_NAME,
    APP_VERSION,
    BUILD_NUMBER,
    COMPANY,
    COPYRIGHT,
    WEBSITE,
    BUILD_MODE,
)

# ---------------------------------------------------------
# Backward-compatible constants
# ---------------------------------------------------------

VERSION = APP_VERSION
RELEASE_NAME = BUILD_MODE
DEVELOPER = COMPANY

# ---------------------------------------------------------
# Derived values
# ---------------------------------------------------------

FULL_VERSION = f"{APP_VERSION} (Build {BUILD_NUMBER})"
WINDOW_TITLE = f"{APP_NAME} v{APP_VERSION}"