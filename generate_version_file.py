"""
=========================================================
Version File Generator
LMS Attendance Automation System
=========================================================

Generates version_info.txt — the Win32 VERSIONINFO resource file
that both desktop.spec and LMSAutomation.spec embed into the .exe
via `version=VERSION_FILE`.

WHY THIS EXISTS (change note, 2026-08-15):
    version_info.txt was previously a static, hand-maintained file
    with no script producing it, so it could silently drift out of
    sync with build_info.APP_VERSION — which is exactly how the
    8.0.0 vs 8.1.0 mismatch happened. This script makes version_info.py
    / build_info.py the single source of truth and (re)generates
    version_info.txt from them.

USAGE:
    Run this from the project root before every PyInstaller build:

        python generate_version_file.py

    Then build as usual:

        pyinstaller desktop.spec
"""

from PyInstaller.utils.win32.versioninfo import (
    VSVersionInfo,
    FixedFileInfo,
    StringFileInfo,
    StringTable,
    StringStruct,
    VarFileInfo,
    VarStruct,
)

from version_info import (
    FILE_VERSION,
    PRODUCT_VERSION,
    PRODUCT_NAME,
    COMPANY_NAME,
    COPYRIGHT_TEXT,
)
from build_info import APP_VERSION


OUTPUT_FILE = "version_info.txt"


def build_version_info():
    return VSVersionInfo(
        ffi=FixedFileInfo(
            filevers=FILE_VERSION,
            prodvers=PRODUCT_VERSION,
            mask=0x3F,
            flags=0x0,
            OS=0x40004,
            fileType=0x1,
            subtype=0x0,
            date=(0, 0),
        ),
        kids=[
            StringFileInfo(
                [
                    StringTable(
                        "040904B0",
                        [
                            StringStruct("CompanyName", COMPANY_NAME),
                            StringStruct("FileDescription", PRODUCT_NAME),
                            StringStruct("FileVersion", APP_VERSION),
                            StringStruct("InternalName", "LMS Automation"),
                            StringStruct("LegalCopyright", COPYRIGHT_TEXT),
                            StringStruct("OriginalFilename", "LMS Automation.exe"),
                            StringStruct("ProductName", PRODUCT_NAME),
                            StringStruct("ProductVersion", APP_VERSION),
                        ],
                    )
                ]
            ),
            VarFileInfo([VarStruct("Translation", [1033, 1200])]),
        ],
    )


if __name__ == "__main__":
    info = build_version_info()

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(str(info))

    print(f"✓ {OUTPUT_FILE} generated for version {APP_VERSION}")
