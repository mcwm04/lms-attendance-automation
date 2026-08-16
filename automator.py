from config.config_manager import ConfigManager
from logger import AppLogger
from browser_manager import BrowserManager
from datetime import datetime
import re
import time


from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    WebDriverException,
    NoSuchWindowException,
    TimeoutException,
    NoSuchElementException,
    StaleElementReferenceException,
    ElementClickInterceptedException,
    ElementNotInteractableException,
)


from exceptions import (
    InvalidCredentialsError,
    LoginTimeoutError,
    LMSUnavailableError,
    BrowserClosedError,
    BrowserNavigationError,
    AutomationError,
    AttendanceLoadError,
    AttendanceSubmissionError,
)


class MoodleAutomator:

    def __init__(self, username, password, headless=True, log_queue=None):
        self.username = username
        self.password = password
        self.headless = headless
        self.driver = None
        self.wait = None
        self.log_queue = log_queue
        self.logger = AppLogger.get_logger()

    def log(self, msg):
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted = f"[{timestamp}] {msg}"
        if self.log_queue:
            self.log_queue.put(formatted)
        self.logger.info(msg)

    # =========================
    def start_browser(self):
        manager = BrowserManager()

        self.driver = manager.create_driver()

        self.wait = WebDriverWait(self.driver, 30)


    # =========================
    def login(self):
        try:
            base_url = ConfigManager.get("lms", "url")
            self.driver.get(f"{base_url}/login/index.php")
            
            self.wait.until(
                EC.presence_of_element_located((By.NAME, "username"))
            )

            self.driver.find_element(By.NAME, "username").send_keys(self.username)
            self.driver.find_element(By.NAME, "password").send_keys(self.password)

            self.driver.find_element(By.XPATH, "//input[@type='submit']").click()

            time.sleep(3)

            current_url = (self.driver.current_url or "").lower()
            page_source = (self.driver.page_source or "").lower()

            # --------------------------------------------------
            # Detect explicit LMS login errors first
            # --------------------------------------------------
            login_error_selectors = [
                "#loginerrormessage",
                ".loginerrors",
                ".alert-danger",
                '[role="alert"]',
            ]

            for selector in login_error_selectors:
                try:
                    error_element = self.driver.find_element(By.CSS_SELECTOR, selector)

                    if error_element.is_displayed():
                        error_text = error_element.text.strip()

                        if error_text:
                            self.log(f"❌ LMS login failed: {error_text}")

                        raise InvalidCredentialsError(
                            "Invalid LMS username or password."
                        )

                except NoSuchElementException:
                    continue


            # --------------------------------------------------
            # Verify successful navigation away from login page
            # --------------------------------------------------
            if "/login/index.php" not in current_url:
                self.log("✅ Login successful")
                return True


            # --------------------------------------------------
            # Still on login page = authentication failed
            # --------------------------------------------------
            self.log("❌ Login verification failed.")
            self.log("❌ LMS is still displaying the login page.")

            raise InvalidCredentialsError(
                "Invalid LMS username or password."
            )

        except TimeoutException as e:

            title = self.driver.title.lower()

            if "privacy" in title:
                raise LMSUnavailableError(
                    "The LMS website could not be opened because of an SSL/Privacy certificate warning."
                ) from e

            raise LoginTimeoutError(
                "The LMS login page did not load within the configured timeout."
            ) from e

        except NoSuchWindowException as e:
            raise BrowserClosedError(
                "The browser was closed during login."
            ) from e

        except WebDriverException as e:
            raise BrowserNavigationError(
                "The browser encountered an unexpected error during login."
            ) from e

    # =========================
    def open_dashboard(self):
        base_url = ConfigManager.get("lms", "url")
        self.driver.get(f"{base_url}/my/")

    # =========================
    def open_course(self, course_url):
        self.log(f"Opening course: {course_url}")
        self.driver.get(course_url)
        time.sleep(2)

    def extract_course_id(self, url):
        return url.split("id=")[-1]

    # =========================
    def open_attendance_via_url(self, course_url):
        course_id = self.extract_course_id(course_url)
        base_url = ConfigManager.get("lms", "url")
        url = f"{base_url}/course/attendance/?id={course_id}"
        
        self.log(f"Opening attendance page: {url}")
        self.driver.get(url)

        time.sleep(3)

        # ✅ ADD THIS HERE (IMPORTANT)
        self.driver.execute_script("""
            document.body.classList.remove('modal-open');
            let overlays = document.querySelectorAll('.modal, .overlay, .backdrop');
            overlays.forEach(e => e.remove());
        """)

    # =========================
    def turn_editing_on(self):

        try:
            btns = self.driver.find_elements(
                By.XPATH,
                "//button[contains(.,'Turn editing on')]"
            )

            if btns:
                btns[0].click()
                self.log("Editing enabled")

        except NoSuchWindowException:
            raise BrowserClosedError(
                "The browser was closed while enabling editing."
            )

        except WebDriverException:
            self.log("Editing mode could not be enabled. Continuing...")

    # =========================
    def get_courses(self):
        courses = []
        self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))

        rows = self.driver.find_elements(By.CSS_SELECTOR, "table tbody tr")

        for row in rows:
            links = row.find_elements(By.TAG_NAME, "a")
            if links:
                name = links[0].text.strip()
                url = links[0].get_attribute("href")
                if name and url:
                    courses.append({"name": name, "url": url})

        return courses

    # =========================
    def get_all_student_ids(self, course_id):
        ids = []
        base_url = ConfigManager.get("lms", "url")
        url = f"{base_url}/course/attendance/Summary.php?id={course_id}"
        self.driver.get(url)
        time.sleep(2)

        checkboxes = self.driver.find_elements(By.CSS_SELECTOR, "table input[type='checkbox'][value]")

        for cb in checkboxes:
            val = cb.get_attribute("value")
            if val and val.isdigit():
                ids.append(val)

        self.log(f"Collected {len(ids)} student IDs")
        return ids

    # =========================
    def get_marked_dates(self, course_id):
        marked = set()
        page_index = 0

        base_url = ConfigManager.get("lms", "url")
        url = f"{base_url}/course/attendance/Summary.php?id={course_id}"
        self.driver.get(url)

        while True:
            time.sleep(2)

            labels = self.driver.find_elements(By.CSS_SELECTOR, "thead th label[data-original-title]")

            for l in labels:
                tooltip = l.get_attribute("data-original-title")
                if tooltip:
                    clean = tooltip.replace("<br>", " ").strip()
                    marked.add(clean)

            next_btn = self.driver.find_elements(By.XPATH, f"//a[@onclick='page({page_index + 1})']")

            if not next_btn:
                break

            page_index += 1
            self.driver.execute_script(f"page({page_index})")
            time.sleep(2)

        self.log(f"Found {len(marked)} sessions")
        return marked

    # =========================
    def get_marked_sessions(self, course_id):
        """
        Retrieve all marked attendance sessions for a course.

        Returns:
            [
                {
                    "datetime": "...",
                    "lid": "12345"
                }
            ]
        """

        sessions = []
        page_index = 0

        try:

            url = (
                f"https://lms.uaf.edu.pk/course/attendance/"
                f"Summary.php?id={course_id}"
            )

            self.log("Opening attendance summary...")

            self.driver.get(url)

            while True:

                self.wait.until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "thead")
                    )
                )

                header_count = len(
                    self.driver.find_elements(
                        By.CSS_SELECTOR,
                        "thead th",
                    )
                )

                for index in range(header_count):

                    header = self.driver.find_elements(
                        By.CSS_SELECTOR,
                        "thead th",
                    )[index]

                    labels = header.find_elements(
                        By.CSS_SELECTOR,
                        "label[data-original-title]"
                    )

                    if not labels:
                        continue

                    tooltip = (
                        labels[0]
                        .get_attribute("data-original-title")
                        or ""
                    ).strip()

                    if not tooltip:
                        continue

                    clean_dt = (
                        tooltip
                        .replace("<br>", " ")
                        .replace("<br/>", " ")
                        .replace("<br />", " ")
                        .strip()
                    )
                    
                    lid = None

                    links = header.find_elements(
                        By.XPATH,
                        ".//a[contains(@href,'lid=')]"
                    )

                    if links:

                        href = links[0].get_attribute("href")

                        match = re.search(
                            r"lid=(\d+)",
                            href,
                        )

                        if match:
                            lid = match.group(1)

                    sessions.append(
                        {
                            "datetime": clean_dt,
                            "lid": lid,
                        }
                    )

                next_page = self.driver.find_elements(
                    By.XPATH,
                    f"//a[@onclick='page({page_index + 1})']"
                )

                if not next_page:
                    break

                old_table = self.driver.find_element(
                    By.CSS_SELECTOR,
                    "thead"
                )

                page_index += 1

                self.log(
                    f"Loading attendance page {page_index + 1}..."
                )

                self.driver.execute_script(
                    f"page({page_index})"
                )

                self.wait.until(
                    EC.staleness_of(old_table)
                )

                self.wait.until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "thead")
                    )
                )

            self.log(
                f"Total attendance sessions found: {len(sessions)}"
            )

            return sessions

        except TimeoutException as e:

            raise AttendanceLoadError(
                "Timed out while loading attendance sessions."
            ) from e

        except Exception as e:

            raise AttendanceLoadError(
                "Unable to retrieve attendance sessions."
            ) from e

    # =========================
    def build_student_map(self):
        student_map = {}

        rows = self.driver.find_elements(By.CSS_SELECTOR, "table tr")

        for row in rows:
            text = row.text
            match = re.search(r"\d{4}-ag-\d{4}", text)

            if not match:
                continue

            ag = match.group(0).strip().lower()

            radios = row.find_elements(By.CSS_SELECTOR, "input[type='radio']")
            if not radios:
                continue

            name_attr = radios[0].get_attribute("name")
            student_map[ag] = name_attr

        return student_map

    # =========================
    def fill_attendance_form(self, config):

        wait = self.wait

        # -------------------------
        # Type
        # -------------------------

        type_box = wait.until(
            EC.element_to_be_clickable((By.ID, "type"))
        )

        Select(type_box).select_by_value(config["type"])

        time.sleep(0.3)

        # -------------------------
        # Date
        # -------------------------

        date_box = wait.until(
            EC.element_to_be_clickable((By.ID, "date"))
        )

        self.driver.execute_script(
            """
            arguments[0].removeAttribute('max');
            arguments[0].value = arguments[1];
            arguments[0].dispatchEvent(new Event('change',{bubbles:true}));
            """,
            date_box,
            config["date"],
        )

        time.sleep(0.3)

        # -------------------------
        # Time
        # -------------------------

        time_box = wait.until(
            EC.element_to_be_clickable((By.ID, "timing"))
        )

        self.driver.execute_script(
            """
            arguments[0].value = arguments[1];
            arguments[0].dispatchEvent(new Event('input',{bubbles:true}));
            arguments[0].dispatchEvent(new Event('change',{bubbles:true}));
            """,
            time_box,
            config["time"],
        )

        # Verify value
        actual = time_box.get_attribute("value")

        if actual != config["time"]:
            raise AutomationError(
                f"Time not accepted. Expected '{config['time']}', got '{actual}'."
            )

        time.sleep(0.3)

        # -------------------------
        # Duration
        # -------------------------

        Select(
            wait.until(
                EC.element_to_be_clickable((By.ID, "lectiming"))
            )
        ).select_by_value(str(config["duration"]))

        time.sleep(0.3)

        # -------------------------
        # Number of lectures
        # -------------------------

        Select(
            wait.until(
                EC.element_to_be_clickable((By.ID, "class"))
            )
        ).select_by_value("1")

        time.sleep(0.5)

    # =========================
    def mark_attendance(self, excel_map):
        student_map = self.build_student_map()

        # Click "Absent" safely
        absent_btn = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//th[contains(text(),'Absent')]//input"))
        )

        self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", absent_btn)
        time.sleep(0.5)

        try:
            absent_btn.click()
        except (ElementClickInterceptedException, ElementNotInteractableException):
            self.driver.execute_script("arguments[0].click();", absent_btn)

        time.sleep(1)

        # Mark students
        for ag, status in excel_map.items():
            ag = ag.strip().lower()

            if ag in student_map:
                name_attr = student_map[ag]
                selector = f"//input[@name='{name_attr}' and @value='{status}']"

                try:
                    element = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, selector))
                    )

                    self.driver.execute_script(
                        "arguments[0].scrollIntoView({block:'center'});", element
                    )
                    time.sleep(0.2)

                    try:
                        element.click()
                    except (ElementClickInterceptedException, ElementNotInteractableException):
                        self.driver.execute_script("arguments[0].click();", element)

                except Exception as e:
                    self.log(f"⚠️ Failed to click {ag}: {e}")

    # =========================
    def submit_attendance(self):

        submit_btn = WebDriverWait(self.driver, 20).until(
            EC.presence_of_element_located((By.ID, "submit"))
        )

        self.driver.execute_script(
            "arguments[0].scrollIntoView({block:'center'});",
            submit_btn,
        )

        try:
            submit_btn.click()

        except Exception as e:
            self.log(f"Normal click failed: {type(e).__name__}")

            self.driver.execute_script(
                "arguments[0].click();",
                submit_btn,
            )

            self.log("JavaScript click executed.")

        time.sleep(3)

    # =========================
    def run_attendance(self, excel_map, config):
        
        try:
            self.fill_attendance_form(config)
            self.mark_attendance(excel_map)
            self.submit_attendance()

            AppLogger.get_logger().info("Attendance submitted successfully.")

        except Exception as e:
            raise AutomationError(
                f"Attendance automation failed: {str(e)}"
            ) from e

    # =========================
    def close(self):
        if self.driver:
            self.driver.quit()
