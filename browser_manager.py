"""
=========================================================
Browser Manager
LMS Attendance Automation Version 8.1
=========================================================

CHANGE NOTE (2026-08-15):
    _chrome_options() was missing the SSL/certificate tolerance
    flags that _edge_options() already had. Since create_driver()
    tries Chrome first, any environment where Chrome is the
    installed browser hit lms.uaf.edu.pk's certificate warning
    interstitial and timed out there (surfaced as
    LMSUnavailableError: "...SSL/Privacy certificate warning"),
    never falling through to the working Edge path. Added the
    same three arguments + acceptInsecureCerts capability that
    Edge already uses.
=========================================================
"""
from exceptions import BrowserStartupError

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService

from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.edge.service import Service as EdgeService

from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager

from config.config_manager import ConfigManager
from logger import AppLogger


class BrowserManager:

    def __init__(self):
        self.logger = AppLogger.get_logger()

    # --------------------------------------------------
    # Chrome Options
    # --------------------------------------------------

    def _chrome_options(self):

        options = ChromeOptions()

        if ConfigManager.get("browser", "headless"):
            options.add_argument("--headless=new")

        if ConfigManager.get("browser", "window_maximized"):
            options.add_argument("--start-maximized")

        options.add_argument("--disable-gpu")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--disable-notifications")

        # SSL / Certificate handling
        # (previously only present on Edge — Chrome hit
        # lms.uaf.edu.pk's certificate warning page and timed
        # out there without these)
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--ignore-ssl-errors")
        options.add_argument("--allow-running-insecure-content")

        # Accept invalid certificates
        options.set_capability("acceptInsecureCerts", True)

        return options

    # --------------------------------------------------
    # Edge Options
    # --------------------------------------------------

    def _edge_options(self):

        options = EdgeOptions()

        if ConfigManager.get("browser", "headless"):
            options.add_argument("--headless=new")

        if ConfigManager.get("browser", "window_maximized", True):
            options.add_argument("--start-maximized")

        options.add_argument("--disable-gpu")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--disable-notifications")

        # SSL / Certificate handling
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--ignore-ssl-errors")
        options.add_argument("--allow-running-insecure-content")

        # Accept invalid certificates
        options.set_capability("acceptInsecureCerts", True)

        return options

    # --------------------------------------------------
    # Create Driver
    # --------------------------------------------------

    def create_driver(self):

        # --------------------------------------------------
        # Try Google Chrome
        # --------------------------------------------------

        try:

            driver = webdriver.Chrome(
                service=ChromeService(
                    ChromeDriverManager().install()
                ),
                options=self._chrome_options()
            )

            return driver

        except Exception as chrome_error:

            self.logger.warning(
                f"Google Chrome unavailable: {chrome_error}"
            )

        # --------------------------------------------------
        # Try Microsoft Edge
        # --------------------------------------------------

        try:

            self.logger.info("Trying Microsoft Edge...")

            driver = webdriver.Edge(
                service=EdgeService(
                    EdgeChromiumDriverManager().install()
                ),
                options=self._edge_options()
            )

            self.logger.info("Microsoft Edge started successfully.")

            return driver

        except Exception as edge_error:

            self.logger.error(
                f"Microsoft Edge unavailable: {edge_error}"
            )

        # --------------------------------------------------
        # Both browsers failed
        # --------------------------------------------------

        raise BrowserStartupError(
            "Unable to launch a supported web browser.\n\n"
            "Google Chrome and Microsoft Edge could not be started.\n\n"
            "Please ensure one of these browsers is installed and updated."
        )
