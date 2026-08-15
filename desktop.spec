# -*- mode: python ; coding: utf-8 -*-

import os
from PyInstaller.utils.hooks import collect_all

# ==========================================================
# Project Configuration
# ==========================================================
#
# CHANGE NOTES (2026-08-15):
#   - Added collect_all("webdriver_manager") — without this, frozen
#     builds fail silently at "Load Courses" because Selenium can't
#     fetch/locate ChromeDriver/EdgeDriver at runtime.
#   - Added collect_all("cryptography") — CredentialManager's Fernet
#     encryption depends on it; not reliably auto-detected otherwise.
#   - Added collect_all("openpyxl") — pandas.read_excel() needs it as
#     the .xlsx engine; the attendance workbook upload would fail.
#   - Wired runtime_hooks.py into runtime_hooks=[...] — it was defined
#     but never registered, so its UTF-8/console fix never actually
#     ran in the frozen build.
#   - console changed True -> False: this is the shipped desktop GUI
#     (pywebview) entry point, so a console window popping up behind
#     it is not desired for end users. Set back to True if you want
#     the debug console during testing.
#
# ==========================================================

PROJECT_ROOT = os.path.abspath(".")

APP_NAME = "LMS Automation"

ICON_FILE = os.path.join(PROJECT_ROOT, "assets", "app.ico")
VERSION_FILE = os.path.join(PROJECT_ROOT, "version_info.txt")

# ==========================================================
# Collect Package Resources
# ==========================================================

gradio_datas, gradio_binaries, gradio_hidden = collect_all("gradio")

groovy_datas, groovy_binaries, groovy_hidden = collect_all("groovy")

safehttpx_datas, safehttpx_binaries, safehttpx_hidden = collect_all("safehttpx")

selenium_datas, selenium_binaries, selenium_hidden = collect_all("selenium")

webview_datas, webview_binaries, webview_hidden = collect_all("webview")

webdriver_manager_datas, webdriver_manager_binaries, webdriver_manager_hidden = collect_all("webdriver_manager")

cryptography_datas, cryptography_binaries, cryptography_hidden = collect_all("cryptography")

openpyxl_datas, openpyxl_binaries, openpyxl_hidden = collect_all("openpyxl")

# ==========================================================
# Analysis
# ==========================================================

a = Analysis(
    ["desktop.py"],
    pathex=[PROJECT_ROOT],

    binaries=
        gradio_binaries +
        groovy_binaries +
        safehttpx_binaries +
        selenium_binaries +
        webview_binaries +
        webdriver_manager_binaries +
        cryptography_binaries +
        openpyxl_binaries,

    datas=[
        ("assets", "assets"),
        ("config", "config"),
    ] +
        gradio_datas +
        groovy_datas +
        safehttpx_datas +
        selenium_datas +
        webview_datas +
        webdriver_manager_datas +
        cryptography_datas +
        openpyxl_datas,

    hiddenimports=[
        "pandas",
        "webview",
    ] +
        gradio_hidden +
        groovy_hidden +
        safehttpx_hidden +
        selenium_hidden +
        webview_hidden +
        webdriver_manager_hidden +
        cryptography_hidden +
        openpyxl_hidden,

    hookspath=[],
    hooksconfig={},
    runtime_hooks=["runtime_hooks.py"],

    excludes=[
        "matplotlib",
        "scipy",
        "IPython",
        "jupyter",
        "notebook",
        "torch",
        "torchvision",
    ],

    noarchive=False,
)

# ==========================================================
# Python Archive
# ==========================================================

pyz = PYZ(a.pure)

# ==========================================================
# Executable
# ==========================================================

exe = EXE(
    pyz,

    a.scripts,

    a.binaries,

    a.datas,

    [],

    name=APP_NAME,

    version=VERSION_FILE,

    icon=ICON_FILE,

    console=False,

    debug=False,

    bootloader_ignore_signals=False,

    strip=False,

    upx=False,

    upx_exclude=[],

    runtime_tmpdir=None,

    disable_windowed_traceback=False,

    argv_emulation=False,

    target_arch=None,

    codesign_identity=None,

    entitlements_file=None,
)
