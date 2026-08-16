"""
=========================================================
Desktop Launcher
LMS Attendance Automation System
Version 8
=========================================================
"""
import ctypes
import socket
import sys
import threading
import time
import tkinter as tk
from pathlib import Path
from tkinter import messagebox
from bootstrap import Bootstrap
from app_info import WINDOW_TITLE

import webview

from logger import AppLogger
from exceptions import BrowserStartupError
from app import launch_app
from path_manager import PathManager

log = AppLogger.get_logger()


def start_server():
    """Start the Gradio server."""
    try:
        launch_app()
    except BrowserStartupError:
        raise
    except Exception:
        log.exception("Gradio server failed to start.")
        raise

def wait_for_server(host="127.0.0.1", port=7860, timeout=30):
    """
    Wait until the Gradio server is accepting TCP connections.
    Returns True if ready, otherwise False.
    """

    log.info("Waiting for Gradio server...")

    start = time.time()

    while time.time() - start < timeout:

        try:
            with socket.create_connection((host, port), timeout=1):
                log.info("✓ Gradio server is ready.")
                return True

        except OSError:
            time.sleep(0.2)

    log.error("Timed out waiting for Gradio server.")
    return False


# ==========================================================
# WINDOWS TASKBAR / TITLE BAR ICON
# ==========================================================
#
# pywebview's `icon=` argument on webview.start() only has an
# effect on the GTK/Qt backends (Linux). On Windows, pywebview
# uses the EdgeChromium backend and exposes no supported way to
# set the window icon — the OS just shows whatever icon is
# embedded in the running process (python.exe / pythonw.exe),
# which is why the Python logo appears instead of our own.
#
# Fix: once the window exists, find its handle and push our own
# icon onto it directly via the WM_SETICON message. This must
# run in webview's own post-start callback (`func=`) so the
# window is guaranteed to exist by the time we look for it.
#
# NOTE: LoadImageW with IMAGE_ICON expects a real .ico file.
# A .bmp will not load correctly here — convert wizard_small.bmp
# to wizard_small.ico first (see convert_icon.py).

WM_SETICON = 0x0080
ICON_SMALL = 0
ICON_BIG = 1
IMAGE_ICON = 1
LR_LOADFROMFILE = 0x00000010
LR_DEFAULTSIZE = 0x00000040


def set_windows_taskbar_icon(icon_path: Path, window_title: str, retries: int = 20):
    """
    Set the taskbar/title-bar icon on Windows for the pywebview
    window. No-op on non-Windows platforms.
    """

    if sys.platform != "win32":
        return

    if not icon_path.exists():
        log.warning(f"Icon file not found, skipping: {icon_path}")
        return

    user32 = ctypes.windll.user32

    hwnd = 0

    for _ in range(retries):
        hwnd = user32.FindWindowW(None, window_title)
        if hwnd:
            break
        time.sleep(0.25)

    if not hwnd:
        log.warning("Could not find window handle to set taskbar icon.")
        return

    hicon = user32.LoadImageW(
        0,
        str(icon_path),
        IMAGE_ICON,
        0,
        0,
        LR_LOADFROMFILE | LR_DEFAULTSIZE,
    )

    if not hicon:
        log.warning(f"Failed to load icon: {icon_path}")
        return

    user32.SendMessageW(hwnd, WM_SETICON, ICON_SMALL, hicon)
    user32.SendMessageW(hwnd, WM_SETICON, ICON_BIG, hicon)

    log.info("✓ Taskbar/title-bar icon applied.")


def run():

    Bootstrap.initialize()

    log.info("Starting Gradio server...")

    threading.Thread(
        target=start_server,
        daemon=True
    ).start()

    if not wait_for_server():

        raise RuntimeError(
            "Gradio server failed to start within 30 seconds."
        )

    log.info("Opening desktop window...")

    icon_path = Path(PathManager.asset("wizard_small.ico"))

    webview.create_window(
        title=WINDOW_TITLE,
        url="http://127.0.0.1:7860",
        width=1200,
        height=800,
        resizable=True
    )

    webview.start(
        func=lambda: set_windows_taskbar_icon(icon_path, WINDOW_TITLE),
    )

    log.info("Application closed.")


if __name__ == "__main__":

    try:
        run()

    except BrowserStartupError as e:

        log.exception("Browser startup failed.")

        root = tk.Tk()
        root.withdraw()

        messagebox.showerror(
            "Browser Error",
            str(e)
        )

        root.destroy()

    except Exception:

        log.exception("Unhandled application exception.")

        root = tk.Tk()
        root.withdraw()

        messagebox.showerror(
            "Application Error",
            "An unexpected error occurred.\n\n"
            "Please check the Logs folder for more information."
        )

        root.destroy()

        raise
