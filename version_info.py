"""
=========================================================
Version Information
LMS Attendance Automation System
Version 8
=========================================================
"""

from build_info import (
    APP_VERSION,
    BUILD_NUMBER,
    COMPANY,
    COPYRIGHT,
    APP_NAME,
)


def version_tuple():
    """
    Returns a version tuple suitable for PyInstaller.
    """

    parts = APP_VERSION.split(".")

    while len(parts) < 4:
        parts.append("0")

    return tuple(int(x) for x in parts)


FILE_VERSION = version_tuple()

PRODUCT_VERSION = FILE_VERSION

PRODUCT_NAME = APP_NAME

COMPANY_NAME = COMPANY

COPYRIGHT_TEXT = COPYRIGHT

BUILD = BUILD_NUMBER