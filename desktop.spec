# -*- mode: python ; coding: utf-8 -*-

import os
from PyInstaller.utils.hooks import collect_all

# ==========================================================
# Project Configuration
# ==========================================================
#
# CHANGE NOTES (2026-08-16):
#   - Switched from ONEFILE to ONEDIR build.
#     Previous EXE() received a.binaries/a.datas directly with no
#     exclude_binaries=True — every launch had to re-extract the
#     entire bundle (Gradio + pandas + selenium + cryptography +
#     webdriver_manager + all DLLs) into a fresh _MEIPASS temp
#     folder before desktop.py even started running. On a stack
#     this heavy that's the dominant cause of the ~1 min delay
#     before the login screen appeared. Onedir extracts once at
#     BUILD time; launches just load already-unpacked files.
#     Ship the resulting dist/LMS Automation/ FOLDER inside the
#     Inno Setup/NSIS installer — end users still get one .exe
#     to double-click, nothing changes for them.
#   - Added excludes for PyQt5/PySide2/PySide6/PyQt6, tkinter's
#     own test suite, unittest, and doctest. None of these are
#     imported by this app; they get swept into the build as
#     optional/transitive extras of Gradio's dependency tree
#     (Gradio can lazy-import Qt bindings for certain plot
#     backends we never use) and inflate both build size and
#     onedir folder size for no benefit.
#   - All collect_all() packages (gradio, groovy, safehttpx,
#     selenium, webview, webdriver_manager, cryptography,
#     openpyxl) were individually verified against app.py /
#     automator.py / browser_manager.py / credential_manager.py
#     — every one is actually imported/used. Nothing removed
#     from that list; see the note at the bottom of this file
#     for how to find further, app-specific bloat safely.
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
        # Already unused — data science / notebook stack
        "matplotlib",
        "scipy",
        "IPython",
        "jupyter",
        "notebook",
        "torch",
        "torchvision",

        # GUI toolkits — this app uses pywebview (EdgeChromium
        # backend on Windows), never Qt. These occasionally get
        # pulled in as optional plotting/display backends by
        # packages in Gradio's dependency tree.
        "PyQt5",
        "PyQt6",
        "PySide2",
        "PySide6",

        # Stdlib test/doc modules — never imported at runtime,
        # only bloat the archive.
        "unittest",
        "doctest",
        "pydoc_data",
        "test",
        "tkinter.test",
    ],

    noarchive=False,
)

# ==========================================================
# Python Archive
# ==========================================================

pyz = PYZ(a.pure)

# ==========================================================
# Executable (ONEDIR — binaries/datas excluded here,
# collected separately below by COLLECT)
# ==========================================================

exe = EXE(
    pyz,

    a.scripts,

    [],

    exclude_binaries=True,

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

# ==========================================================
# Collect — bundles binaries/datas into dist/LMS Automation/
# alongside the .exe. This is what makes it ONEDIR: everything
# is unpacked once at build time instead of re-extracted into
# a temp folder on every launch.
# ==========================================================

coll = COLLECT(
    exe,

    a.binaries,

    a.datas,

    strip=False,

    upx=False,

    upx_exclude=[],

    name=APP_NAME,
)