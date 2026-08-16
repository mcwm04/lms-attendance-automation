# -*- mode: python ; coding: utf-8 -*-

import os
from PyInstaller.utils.hooks import collect_all

# ==========================================================
# Project Configuration
# ==========================================================

PROJECT_ROOT = os.path.abspath(".")

APP_NAME = "LMS Attendance Automation"

ICON_FILE = os.path.join(PROJECT_ROOT, "assets", "app.ico")
VERSION_FILE = os.path.join(PROJECT_ROOT, "version_info.txt")
RUNTIME_HOOK = os.path.join(PROJECT_ROOT, "runtime_hooks.py")

# ==========================================================
# Collect Package Resources
# ==========================================================

gradio_datas, gradio_binaries, gradio_hidden = collect_all("gradio")
groovy_datas, groovy_binaries, groovy_hidden = collect_all("groovy")
safehttpx_datas, safehttpx_binaries, safehttpx_hidden = collect_all("safehttpx")
selenium_datas, selenium_binaries, selenium_hidden = collect_all("selenium")
webview_datas, webview_binaries, webview_hidden = collect_all("webview")

# ==========================================================
# Analysis
# ==========================================================

a = Analysis(
    ["desktop.py"],
    pathex=[PROJECT_ROOT],

    binaries=(
        gradio_binaries +
        groovy_binaries +
        safehttpx_binaries +
        selenium_binaries +
        webview_binaries
    ),

    datas=[
        ("assets", "assets"),
        ("config/defaults.json", "config"),
    ] +
    gradio_datas +
    groovy_datas +
    safehttpx_datas +
    selenium_datas +
    webview_datas,

    hiddenimports=[
        "pandas",
        "webview",
    ] +
    gradio_hidden +
    groovy_hidden +
    safehttpx_hidden +
    selenium_hidden +
    webview_hidden,

    hookspath=[],
    hooksconfig={},

    runtime_hooks=[
        RUNTIME_HOOK,
    ],

    excludes=[
        "matplotlib",
        "scipy",
        "torch",
        "torchvision",
        "torchaudio",
        "ultralytics",
        "transformers",
        "playwright",
        "IPython",
        "jupyter",
        "notebook",
        "pytest",
        "test",
        "tests",
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

    icon=ICON_FILE,

    version=VERSION_FILE,

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