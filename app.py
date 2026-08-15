### 📄 app.py (LOCAL VERSION — GRADIO 6.12.0 COMPATIBLE)

import gradio as gr
import pandas as pd
import threading
from datetime import datetime, timedelta
from queue import Queue, Empty
from automator import MoodleAutomator
import os
from logger import AppLogger
from credential_manager import CredentialManager
from path_manager import PathManager
from pathlib import Path
from course_settings import CourseSettings
from ui.components import section_body, section_card, field_group
from ui.html import section_header, app_footer
from ui.widgets import (
    app_textbox,
    output_box,
    app_dropdown,
    primary_button,
    secondary_button,
    upload_box,
    app_dataframe,
    app_checkbox,
)
from ui.screens.authentication import create_authentication_screen
from ui.screens.dashboard import create_dashboard_screen
from exceptions import (
    LMSAutomationError,

    InvalidCredentialsError,
    LoginTimeoutError,
    LMSUnavailableError,

    BrowserStartupError,
    BrowserClosedError,
    BrowserNavigationError,

    CourseLoadError,
    CourseNotFoundError,

    AttendanceLoadError,
    AttendanceSubmissionError,

    AutomationError,

    ExcelValidationError,
    ExcelFileRequiredError,

    ConfirmationRequiredError,
    NoActiveSessionError,
)

# =========================
# GLOBALS
# =========================
custom_css = PathManager.asset(
    "styles", "theme.css"
).read_text(encoding="utf-8")
courses_list = []
course_data_cache = {}
bot_instance = None
log_queue = Queue()  # Thread-safe queue for live streaming
is_running = False
# ==========================================
# Load saved credentials (if available)
# ==========================================

saved_username, saved_password = CredentialManager.load()

remember_default = bool(saved_username or saved_password)
# =========================
# Error Handler
# =========================

ERROR_MESSAGES = {

    InvalidCredentialsError:
        "❌ Login failed.\n\nThe username or password is incorrect.",

    LoginTimeoutError:
        "❌ Login timed out.\n\nThe LMS login page did not respond.",

    LMSUnavailableError:
        "❌ Unable to connect to the LMS.\n\nThe LMS website is unavailable.",

    BrowserStartupError:
        "❌ Browser could not be started.\n\nPlease ensure Chrome or Edge is installed.",

    BrowserClosedError:
        "❌ Browser was closed before the operation completed.",

    BrowserNavigationError:
        "❌ Unable to navigate inside the LMS.",

    CourseLoadError:
        "❌ Unable to load courses.",

    CourseNotFoundError:
        "❌ The selected course could not be found.",

    AttendanceLoadError:
        "❌ Unable to load attendance information.",

    AttendanceSubmissionError:
        "❌ Unable to submit attendance.\n\n"
        "The attendance form could not be submitted to the LMS.",

    ExcelValidationError:
        "❌ Invalid attendance Excel file.",

    ExcelFileRequiredError:
        "❌ Please upload an attendance Excel file before continuing.",

    ConfirmationRequiredError:
        "❌ Please confirm the preview before starting automation.",

    NoActiveSessionError:
        "❌ No active LMS session.\n\nPlease click 'Load Courses' first.",

    AutomationError:
        "❌ Attendance automation failed.",
}

def handle_application_error(exception):
    """
    Convert application exceptions into user-friendly messages.
    """
    
    return ERROR_MESSAGES.get(
            type(exception),
            "❌ An unexpected error occurred.\n\nPlease check the application log."
        )

# =========================
# LOGGING SYSTEM (LIVE STREAMING)
# =========================
def log_message(message):
    """
    Add a timestamped message to the Live Execution Monitor.
    """

    if message is None:
        return

    timestamp = datetime.now().strftime("%H:%M:%S")

    try:
        message = str(message)
        message = message.encode(
            "utf-8",
            errors="replace"
        ).decode("utf-8")

    except Exception:

        message = "⚠️ Unable to display log message."

    formatted = f"[{timestamp}] {message}"

    log_queue.put(formatted)

    try:
        print(formatted)

    except Exception:
        pass

def get_logs_from_queue():
    """
    Retrieve all pending log messages.
    """

    messages = []

    while True:

        try:
            messages.append(
                log_queue.get_nowait()
            )

        except Empty:
            break

    return messages


def get_course_id(course_name):
    """
    Returns the LMS course ID for the selected course.
    """

    global courses_list, bot_instance

    for course in courses_list:

        if course["name"] == course_name:
            return bot_instance.extract_course_id(course["url"])

    return None

# =========================
# SAFE TIME PARSING
# =========================
def expand_schedule(schedule):
    expanded = []
    for entry in schedule:
        time_str = str(entry["start_time"]).strip()
        if len(time_str.split(":")) == 3:
            time_str = ":".join(time_str.split(":")[:2])
        try:
            base_time = datetime.strptime(time_str, "%H:%M")
        except:
            raise ValueError(f"Invalid time format: '{entry['start_time']}'. Use HH:MM (e.g., 09:00)")

        for i in range(entry["lectures"]):
            lecture_time = (
                base_time + timedelta(minutes=i * entry["duration"])
            ).strftime("%H:%M")
            expanded.append({
                "day": entry["day"],
                "time": lecture_time,
                "type": entry["type"],
                "duration": entry["duration"]
            })
    return expanded

# =========================
# Load COURSES
# =========================
def load_courses(username, password, remember_me):
    global courses_list, course_data_cache, bot_instance

    try:
        log_message("🌐 Starting browser...")

        bot_instance = MoodleAutomator(
            username=username,
            password=password,
            headless=False,
            log_queue=log_queue
        )

        bot_instance.start_browser()
        log_message("✅ Browser started successfully.")

        log_message("🔐 Signing in to LMS...")
        if not bot_instance.login():
            log_message("❌ Login failed.")
            return [], "❌ Login failed", ""

        # --------------------------------------
        # Remember Me
        # --------------------------------------
        if remember_me:
            CredentialManager.save(username, password)
        else:
            CredentialManager.clear()

        log_message("📂 Loading dashboard...")
        bot_instance.open_dashboard()
        log_message("✅ Dashboard loaded.")

        log_message("📚 Retrieving courses...")
        courses = bot_instance.get_courses()

        courses_list = courses

        course_names = [course["name"] for course in courses]

        log_message(f"✅ {len(courses)} courses loaded successfully.")

        marked_text = ""

        return (
            course_names,
            "✅ Courses loaded successfully.",
            marked_text,
        )

    except InvalidCredentialsError as e:

        AppLogger.get_logger().exception(e)

        message = handle_application_error(e)

        log_message(message)

        return [], message, ""


    except LMSAutomationError as e:

        AppLogger.get_logger().exception(e)

        message = handle_application_error(e)

        log_message(message)

        return [], message, ""


    except Exception as e:

        AppLogger.get_logger().exception(e)

        log_message(
            "❌ An unexpected error occurred while loading courses."
        )

        return (
            [],
            "❌ An unexpected error occurred.\n\n"
            "Please check the application log.",
            "",
        )

# =========================
# Generate Lecture Plan
# =========================
def generate_lecture_plan(start_date, end_date, expanded_schedule, holidays):
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    holidays = set(holidays)
    lecture_plan = []
    current = start
    
    while current <= end:
        day_name = current.strftime("%A")
        date_str = current.strftime("%Y-%m-%d")
        
        if day_name in ["Saturday", "Sunday"]:
            current += timedelta(days=1)
            continue
            
        if date_str in holidays:
            current += timedelta(days=1)
            continue
            
        for entry in expanded_schedule:
            if entry["day"] == day_name:
                lecture_plan.append({
                    # ===== Lecture Information =====
                    "date": date_str,
                    "day": day_name,
                    "type": entry["type"],
                    "time": entry["time"],
                    "duration": entry["duration"],

                    # ===== Synchronization Status =====
                    "scheduled": True,
                    "marked_lms": False,
                    "excel_found": False,
                    "ready_upload": False,
                    "missing": False,

                    # ===== Future Extensions =====
                    "student_count": 0,
                    "remarks": ""
                })
        current += timedelta(days=1)
    
    return lecture_plan

# =========================
# Analyze Lecture Status
# =========================
def analyze_lecture_status(
    lecture_plan,
    lms_sessions,
    excel_dates,
):
    """
    Analyze generated lectures against LMS and Excel attendance.

    Parameters
    ----------
    lecture_plan : list
        Generated semester lectures.

    lms_sessions : list
        Enriched LMS sessions. Each item contains:
            day, date, time, type, ...

    excel_dates : set
        Dates found in uploaded Excel.

    Returns
    -------
    lecture_plan, stats
    """

    excel_dates = set(excel_dates)

    # --------------------------------------
    # Build LMS lookup
    # --------------------------------------

    lms_lookup = {
        (s["date"], s["time"])
        for s in lms_sessions
    }

    stats = {
        "total_lectures": len(lecture_plan),
        "already_marked": 0,
        "found_in_excel": 0,
        "ready_upload": 0,
        "missing": 0,
        "excel_only": 0,
    }

    scheduled_dates = set()
    ready_upload_lectures = []

    for lecture in lecture_plan:

        date = lecture["date"]
        time = lecture["time"]

        scheduled_dates.add(date)

        lecture_key = (date, time)

        # -------------------------------
        # Reset flags
        # -------------------------------

        lecture["marked_lms"] = False
        lecture["excel_found"] = False
        lecture["ready_upload"] = False
        lecture["missing"] = False

        # -------------------------------
        # Already marked on LMS
        # -------------------------------

        if lecture_key in lms_lookup:
            lecture["marked_lms"] = True
            stats["already_marked"] += 1

        # -------------------------------
        # Found in Excel
        # -------------------------------

        if date in excel_dates:
            lecture["excel_found"] = True
            stats["found_in_excel"] += 1

        # -------------------------------
        # Determine upload status
        # -------------------------------

        if lecture["marked_lms"]:
            pass

        elif lecture["excel_found"]:
            lecture["ready_upload"] = True
            stats["ready_upload"] += 1

            # Queue this lecture for automation
            ready_upload_lectures.append(lecture)

        else:
            lecture["missing"] = True
            stats["missing"] += 1

    stats["excel_only"] = len(excel_dates - scheduled_dates)

    return (
        lecture_plan,
        stats,
        ready_upload_lectures,
    )

# =========================
# Parse Schedule
# =========================
def parse_schedule(df):
    schedule = []
    valid_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    valid_types = ["Theory", "Practical"]

    for _, row in df.iterrows():
        day = str(row["Day"]).strip()
        time = str(row["Start Time"]).strip()
        lec_type = str(row["Lecture Type"]).strip()
        num_lectures = int(row["No. of Lectures"])
        duration = int(row["Duration (min)"])

        if day not in valid_days:
            raise ValueError(f"Invalid day: {day}")
        if lec_type not in valid_types:
            raise ValueError(f"Invalid lecture type: {lec_type}")
        if num_lectures < 1 or num_lectures > 4:
            raise ValueError(f"Invalid number of lectures for {day}")
        if duration <= 0:
            raise ValueError(f"Invalid duration for {day}")

        schedule.append({
            "day": day,
            "start_time": time,
            "type": lec_type,
            "lectures": num_lectures,
            "duration": duration
        })
    return schedule

# =========================
# Parse Holidays
# =========================
def parse_holidays(holiday_text):
    if not holiday_text:
        return []
    return [d.strip() for d in holiday_text.split(",") if d.strip()]

# =========================
# Read Excel File
# =========================
def read_excel_matrix(file):

    if file is None:
        raise ValueError("Attendance Excel file was not provided.")

    df = pd.read_excel(file.name, header=1)
    df.columns = [str(col).strip() for col in df.columns]
    attendance_by_date = {}

    for col in df.columns[3:]:
        try:
            date_str = pd.to_datetime(col).strftime("%Y-%m-%d")
        except:
            continue
            
        attendance_by_date[date_str] = {}
        for _, row in df.iterrows():
            ag = str(row["AG_NUMBER"]).strip().lower()
            status = str(row[col]).strip().upper()
            if status in ["P", "A", "L"]:
                attendance_by_date[date_str][ag] = status

    return attendance_by_date

# =========================
# Format Report Section
# =========================
def format_report_section(
    title,
    icon,
    items,
    formatter=None,
    empty_message="No records found.",
):
    """
    Generic formatter for report sections.

    Parameters
    ----------
    title : str
        Section title.

    icon : str
        Section icon.

    items : list
        Items to display.

    formatter : callable(index, item) -> str
        Custom formatter for each item.

    empty_message : str
        Message shown when there are no items.
    """

    lines = []

    lines.append("\n══════════════════════════════════════════════════\n")
    lines.append(f"{icon} {title}")
    lines.append("\n══════════════════════════════════════════════════\n")
    lines.append("")

    if not items:

        lines.append(empty_message)
        lines.append("")
        lines.append("Total: 0")
        lines.append("")

        return "\n".join(lines)

    for index, item in enumerate(items, start=1):

        if formatter:

            lines.append(formatter(index, item))

        else:

            lines.append(
                f"{index:02d}. {icon} "
                f"{item['day']:<10} | "
                f"{item['date']} | "
                f"{item['time']} | "
                f"{item['type']}"
            )

    lines.append("")
    lines.append(f"Total: {len(items)}")
    lines.append("")

    return "\n".join(lines)

# =========================
# Format LMS Session
# =========================
def format_lms_session(index, session):

    return (
        f"{index:02d}. ✓ "
        f"{session['day']:<10} | "
        f"{session['date']} | "
        f"{session['time']} | "
        f"{session['type']}"
    )
# =========================
# Enrich LMS Sessions
# =========================
def enrich_lms_sessions(sessions, lecture_plan):

    matched_sessions = []
    extra_sessions = [] 

    lecture_lookup = {
        (lecture["date"], lecture["time"]): lecture
        for lecture in lecture_plan
    }

    for session in sessions:
        
        dt = datetime.strptime(
            session["datetime"],
            "%Y-%m-%d %H:%M:%S"
        )

        date = dt.strftime("%Y-%m-%d")
        time = dt.strftime("%H:%M")

        lecture = lecture_lookup.get((date, time))

        session_info = {
            "day": dt.strftime("%A"),
            "date": date,
            "time": time,
            "type": lecture["type"] if lecture else "Not in Schedule",
            "lid": session["lid"],
            "datetime": session["datetime"],
        }

        if lecture:
            matched_sessions.append(session_info)
        else:
            extra_sessions.append(session_info)

    return matched_sessions, extra_sessions
# =========================
# Get Enriched LMS Sessions
# =========================
def get_enriched_lms_sessions(course_id, sessions):
    """
    Load saved course settings, generate the lecture plan,
    and enrich LMS sessions with lecture information.

    CHANGE NOTE (2026-08-15): previously returned raw `sessions`
    unmodified when no course settings existed yet, but those raw
    dicts only have "datetime"/"lid" — no "day"/"date"/"time"/"type".
    format_lms_session() then crashed with KeyError('day') the first
    time a course was selected before its schedule was saved. Now
    always routes through enrich_lms_sessions() with an empty lecture
    plan, so every session still gets the full shape (falling into
    "extra_sessions" as "Not in Schedule" until a schedule is saved).
    """

    settings = CourseSettings.load(course_id)

    if not settings:
        return enrich_lms_sessions(sessions, [])

    schedule = parse_schedule(
        pd.DataFrame(settings["schedule"])
    )

    expanded = expand_schedule(schedule)

    lecture_plan = generate_lecture_plan(
        settings["start_date"],
        settings["end_date"],
        expanded,
        settings["holidays"],
    )

    return enrich_lms_sessions(
        sessions,
        lecture_plan,
    )
# =========================
# Build Synchronization Report
# =========================
def build_attendance_sync_report(
    course,
    start_date,
    end_date,
    lectures,
    stats,
    marked_sessions,
    student_ids,
):

    output = ""
     # --------------------------------------
    # Group lectures by status
    # --------------------------------------

    already_marked = []
    ready_upload = []
    missing = []

    for lecture in lectures:

        if lecture["marked_lms"]:
            already_marked.append(lecture)

        elif lecture["ready_upload"]:
            ready_upload.append(lecture)

        elif lecture["missing"]:
            missing.append(lecture)

    output += "══════════════════════════════════════════════\n"
    output += "     ATTENDANCE SYNCHRONIZATION REPORT\n"
    output += "══════════════════════════════════════════════\n\n"

    output += f"Course              : {course}\n\n"
    output += f"Semester            : {start_date} → {end_date}\n\n"

    output += "──────────────────────────────────────────────\n"
    output += "SUMMARY\n"
    output += "──────────────────────────────────────────────\n\n"

    output += f"Generated Lectures  : {stats['total_lectures']}\n\n"
    output += f"Marked on LMS       : {stats['already_marked']}\n\n"
    output += f"Found in Excel      : {stats['found_in_excel']}\n\n"
    output += f"Ready for Upload    : {stats['ready_upload']}\n\n"
    output += f"Missing from Excel  : {stats['missing']}\n\n"
    output += f"Extra Excel Dates   : {stats['excel_only']}\n\n"
    output += f"LMS Sessions        : {len(marked_sessions)}\n\n"
    output += f"Students            : {len(student_ids)}\n\n"

    output += "──────────────────────────────────────────────\n"
    output += "LEGEND\n"
    output += "──────────────────────────────────────────────\n\n"

    output += "✓  LECTURES ALREADY MARKED ON LMS\n\n"
    output += "⬆  LECTURES READY FOR UPLOAD\n\n"
    output += "⚪  LECTURES MISSING FROM EXCEL\n\n"

    output += format_report_section(
        title="ALREADY MARKED IN LMS",
        icon="✓",
        items=already_marked,
    )

    output += format_report_section(
        title="LECTURES READY FOR UPLOAD",
        icon="⬆",
        items=ready_upload,
    )

    output += format_report_section(
        title="LECTURES MISSING FROM EXCEL",
        icon="⚪",
        items=missing,
    )

    output += "══════════════════════════════════════════════\n"
    output += "REPORT SUMMARY\n"
    output += "══════════════════════════════════════════════\n\n"

    output += (
        f"Generated : {stats['total_lectures']} \n\n "
        f"Marked : {stats['already_marked']} \n\n"
        f"Ready : {stats['ready_upload']} \n\n"
        f"Missing : {stats['missing']}\n"
    )


    return output
# =========================
# Weekly Schedule Preview
# =========================
def preview_schedule(schedule_df, start_date, end_date, holiday_text, file, course):

    try:

        # --------------------------------------------------
        # Validate course
        # --------------------------------------------------

        course_id = get_course_id(course)

        if not course_id:
            return "❌ Please select a course."

        log_message("🔍 Generating lecture preview...")

        if course_id not in course_data_cache:
            return (
                "❌ LMS data is not available.\n\n"
                "Please select the course again to synchronize LMS data."
            )

        course_info = course_data_cache[course_id]

        # --------------------------------------------------
        # Save course settings
        # --------------------------------------------------

        settings = {
            "start_date": start_date,
            "end_date": end_date,
            "holidays": parse_holidays(holiday_text),
            "schedule": schedule_df.to_dict("records")
        }

        log_message("💾 Saving course settings...")
        CourseSettings.save(course_id, settings)
        log_message("✅ Course settings saved.")

        # --------------------------------------------------
        # Validate Excel
        # --------------------------------------------------

        if file is None:
            log_message("❌ Please upload the attendance Excel file.")
            return (
                "❌ Please upload the attendance Excel file "
                "before generating the preview."
            )

        # --------------------------------------------------
        # Generate semester lectures
        # --------------------------------------------------

        schedule = parse_schedule(schedule_df)
        expanded = expand_schedule(schedule)

        log_message("📖 Reading Excel file...")

        attendance_data = read_excel_matrix(file)

        holidays = parse_holidays(holiday_text)

        lectures = generate_lecture_plan(
            start_date,
            end_date,
            expanded,
            holidays,
        )

        # --------------------------------------------------
        # Read synchronized LMS cache
        # --------------------------------------------------

        lms_sessions = course_info.get("sessions", [])
        extra_sessions = course_info.get("extra_sessions", [])
        student_ids = course_info.get("student_ids", [])

        excel_dates = set(attendance_data.keys())

        # --------------------------------------------------
        # Analyze lecture status
        # --------------------------------------------------

        lectures, stats, ready_upload_lectures = analyze_lecture_status(
            lectures,
            lms_sessions,
            excel_dates,
        )

        # --------------------------------------------------
        # Summary Statistics
        # --------------------------------------------------

        output = build_attendance_sync_report(
            course=course,
            start_date=start_date,
            end_date=end_date,
            lectures=lectures,
            stats=stats,
            marked_sessions=lms_sessions,
            student_ids=student_ids,
        )

        log_message(
            f"✅ Preview generated successfully ({len(lectures)} lectures)."
        )

        return output
    except LMSAutomationError as e:

        AppLogger.get_logger().exception(e)

        message = handle_application_error(e)

        log_message(message)

        return message

    except Exception as e:

        AppLogger.get_logger().exception(e)

        log_message("❌ Unable to generate lecture preview.")

        return (
            "❌ Unable to generate lecture preview.\n\n"
            "Please check the application log."
        )
# =========================
# Course Change Handler
# =========================
def on_course_change(course_name):
    global courses_list, course_data_cache, bot_instance

    try:
        # -----------------------------------------
        # Existing attendance preview
        # -----------------------------------------

        course_id = get_course_id(course_name)

        if not course_id:
            return (
                "Course not found",
                get_empty_schedule(),
                "",
                "",
                "",
                None,
                "",
                False,
                "",
                "",
                "",
                "⚠️ Course not found",
            )
        # -----------------------------------------
        # Synchronize selected course (only once)
        # -----------------------------------------

        if course_id not in course_data_cache:

            log_message("🔄 Synchronizing selected course...")

            selected_course = next(
                c for c in courses_list
                if bot_instance.extract_course_id(c["url"]) == course_id
            )

            (
                _,
                student_ids,
                detailed_sessions,
            ) = prefetch_course_data(
                bot_instance,
                selected_course,
            )

            enriched_sessions, extra_sessions = get_enriched_lms_sessions(
                course_id,
                detailed_sessions,
            )

            course_data_cache[course_id] = {
                "student_ids": student_ids,
                "sessions": enriched_sessions,
                "extra_sessions": extra_sessions,
            }

            log_message("✅ Course synchronization complete.")
        sessions = course_data_cache[course_id]["sessions"]

        # --------------------------------------
        # Get Cached LMS Sessions
        # --------------------------------------

        sessions = course_data_cache[course_id]["sessions"]
        display_sessions = sessions
        extra_sessions = course_data_cache[course_id]["extra_sessions"]

        # --------------------------------------
        # Format Attendance Records
        # --------------------------------------

        if display_sessions or extra_sessions:

            marked_text = ""

            if display_sessions:

                marked_text += format_report_section(
                    title="ALREADY MARKED ATTENDANCE",
                    icon="✓",
                    items=display_sessions,
                    formatter=format_lms_session,
                )

            if extra_sessions:

                marked_text += format_report_section(
                    title="EXTRA LMS SESSIONS",
                    icon="⚠️",
                    items=extra_sessions,
                )

        else:

            marked_text = "No attendance found"

        # -----------------------------------------
        # Load saved course settings
        # -----------------------------------------

        log_message("=" * 60)
        log_message(f"📘 Course changed: {course_name}")


        if course_id:
            log_message(f"🆔 Course ID: {course_id}")

        settings = CourseSettings.load(course_id)

        if settings:

            log_message("📂 Loading saved course settings...")

            schedule_df = pd.DataFrame(settings["schedule"])
            start = settings["start_date"]
            end = settings["end_date"]
            holidays = ", ".join(settings["holidays"])

            log_message("✅ Course settings loaded successfully.")

        else:

            log_message("📝 No saved course settings found.")

            schedule_df = get_empty_schedule()
            start = ""
            end = ""
            holidays = ""

        log_message("=" * 60)

        return (
            marked_text,
            schedule_df,
            start,
            end,
            holidays,
            None,
            "",
            False,
            "",
            "",   # Clear logs_state
            "",   # Clear live_logs
            f"✅ Course selected: {course_name}",
        )

    except Exception as e:
        
        AppLogger.get_logger().exception(e)

        log_message(f"❌ Error: {e}")

        return (
            f"Error: {e}",
            get_empty_schedule(),
            "",
            "",
            "",
            None,   # file
            "",     # preview
            False,  # confirm
            "",     # output
            "",     # logs_state
            "",     # live_logs
            "❌ Error loading course",
        )
# =========================
#  AUTOMATION Inputs Validation
# =========================
def validate_automation_inputs(
    confirm,
    bot,
    file,
    course,
    courses_list,
):
    """
    Validate all inputs before automation begins.
    Returns the selected course object.
    """

    if not confirm:
        raise ConfirmationRequiredError()

    if bot is None:
        raise NoActiveSessionError()

    if file is None:
        raise ExcelFileRequiredError()

    selected_course = next(
        (
            c
            for c in courses_list
            if c["name"] == course
        ),
        None,
    )

    if selected_course is None:
        raise CourseNotFoundError()

    return selected_course

# ==================================================
# PREPARE DATA
# ==================================================

def prepare_execution_data(
    schedule_df,
    start_date,
    end_date,
    holiday_text,
    file,
):
    """
    Prepare all data required before automation begins.
    """

    log_message("🗂 Preparing execution data...")

    schedule = parse_schedule(schedule_df)

    expanded_schedule = expand_schedule(schedule)

    log_message("📖 Reading Excel file...")

    attendance_data = read_excel_matrix(file)

    log_message(
        f"✅ Loaded {len(attendance_data)} attendance dates."
    )

    holidays = parse_holidays(holiday_text)

    log_message(
        f"🎉 Holidays excluded: {len(holidays)}"
    )

    lectures = generate_lecture_plan(
        start_date,
        end_date,
        expanded_schedule,
        holidays,
    )

    log_message(
        f"📅 Generated {len(lectures)} lecture(s)."
    )

    return (
        attendance_data,
        holidays,
        lectures,
    )

# ==================================================
# PREFETCH LMS DATA
# ==================================================
def prefetch_course_data(bot, selected_course):
    """
    Load all LMS data required before attendance automation begins.
    """

    log_message("🔍 Preparing LMS data...")

    course_id = bot.extract_course_id(
        selected_course["url"]
    )

    log_message("👥 Loading student list...")
    student_ids = bot.get_all_student_ids(course_id)

    log_message(
        f"✅ {len(student_ids)} students loaded."
    )

    log_message("📊 Loading attendance records...")
    detailed_sessions = bot.get_marked_sessions(course_id)

    log_message(
        f"✅ {len(detailed_sessions)} attendance sessions loaded."
    )

    return (
        course_id,
        student_ids,
        detailed_sessions,
    )

# ==================================================
# AUTOMATION LOOP
# ==================================================

def execute_automation_loop(
        bot,
        lectures,
        attendance_data,
    ):
        """
        Execute attendance automation.

        This function assumes that every lecture passed to it
        has already been verified as:
            ✓ Found in Excel
            ✓ Not already marked on LMS

        Therefore, no additional validation is performed here.
        """

        total = len(lectures)
        executed = 0

        if total == 0:

            log_message("=" * 60)
            log_message("ℹ️ No lectures require uploading.")
            log_message("=" * 60)

            return (
                executed,
                total,
            )

        log_message("=" * 60)
        log_message("🚀 STARTING ATTENDANCE UPLOAD")
        log_message(f"📚 Lectures to upload : {total}")
        log_message("=" * 60)

        for index, lecture in enumerate(lectures):

            progress = ((index + 1) / total) * 100

            log_message("")
            log_message("=" * 50)
            log_message(
                f"📤 Uploading Lecture {index + 1} of {total}"
            )
            log_message(
                f"📈 Progress : {progress:.1f}%"
            )
            log_message("=" * 50)

            date = lecture["date"]
            time = lecture["time"]

            excel_map = attendance_data[date]

            present = sum(
                status == "P"
                for status in excel_map.values()
            )

            absent = sum(
                status == "A"
                for status in excel_map.values()
            )

            leave = sum(
                status == "L"
                for status in excel_map.values()
            )

            log_message(
                f"📅 {date} | {time} | {lecture['type']}"
            )

            log_message(
                f"👥 Present: {present}   "
                f"Absent: {absent}   "
                f"Leave: {leave}"
            )

            log_message("📝 Recording attendance...")

            bot.run_attendance(
                excel_map=excel_map,
                config=lecture,
            )

            executed += 1

            log_message("✅ Attendance submitted successfully.")

        log_message("")
        log_message("=" * 60)
        log_message("🎉 ATTENDANCE UPLOAD COMPLETED")
        log_message("=" * 60)
        log_message(f"📤 Uploaded Successfully : {executed}")
        log_message(f"📚 Total Upload Requests : {total}")
        log_message("=" * 60)

        return (
            executed,
            total,
        )

# ==================================================
# NAVIGATE
# ==================================================
def navigate_to_attendance_activity(bot, selected_course):
    """
    Navigate to the course attendance activity.
    """

    log_message("🌐 Opening course...")
    bot.open_course(selected_course["url"])
    log_message("✅ Course opened.")

    log_message("✏️ Enabling editing...")
    bot.turn_editing_on()
    log_message("✅ Editing enabled.")

    log_message("📂 Opening attendance activity...")
    bot.open_attendance_via_url(selected_course["url"])
    log_message("✅ Attendance activity opened.")

# ==================================================
# Execution Summary
# ==================================================

def log_execution_summary(
    selected_course,
    lectures,
    student_ids,
    marked_dates,
):
    """
    Display execution summary before automation starts.
    """

    log_message("=" * 60)
    log_message("📊 EXECUTION SUMMARY")
    log_message("=" * 60)

    log_message(f"📚 Course           : {selected_course['name']}")
    log_message(f"📅 Planned Lectures : {len(lectures)}")
    log_message(f"👥 Students         : {len(student_ids)}")
    log_message(f"📝 Already Marked   : {len(marked_dates)}")

    log_message("=" * 60)

# ==================================================
# Completion Summary
# ==================================================

def log_completion_summary(
    executed,
    total,
):
    """
    Display final automation upload statistics.
    """

    success_rate = 0

    if total:
        success_rate = (executed / total) * 100

    log_message("=" * 60)
    log_message("🎉 ATTENDANCE UPLOAD COMPLETED")
    log_message("=" * 60)

    log_message(
        f"📤 Lectures Uploaded : {executed}"
    )

    log_message(
        f"📚 Total to Upload   : {total}"
    )

    log_message(
        f"📈 Success Rate      : {success_rate:.1f}%"
    )

    if executed == total:
        log_message(
            "✅ All ready lectures uploaded successfully."
        )
    else:
        failed = total - executed

        log_message(
            f"⚠️ Uploads not completed : {failed}"
        )

    log_message("=" * 60)

# =========================
# 🚀 MAIN AUTOMATION WITH LIVE STREAMING
# =========================
def run_automation(
    schedule_df,
    start_date,
    end_date,
    holiday_text,
    file,
    course,
    confirm,
    username,
    password,
):
    global bot_instance, courses_list, course_data_cache
    global is_running

    settings = {
        "start_date": start_date,
        "end_date": end_date,
        "holidays": parse_holidays(holiday_text),
        "schedule": schedule_df.to_dict("records")
    }

    course_id = get_course_id(course)

    log_message("💾 Saving course settings...")

    CourseSettings.save(course_id, settings)

    log_message("✅ Course settings saved.")

    bot = bot_instance
    is_running = True

    try:

        selected_course = validate_automation_inputs(
            confirm=confirm,
            bot=bot,
            file=file,
            course=course,
            courses_list=courses_list,
        )

        # ==================================================
        # CLEAR PREVIOUS LOGS
        # ==================================================

        while not log_queue.empty():
            log_queue.get()

        log_message("=" * 50)
        log_message(f"🚀 AUTOMATION STARTED: {selected_course['name']}")
        log_message("=" * 50)

        attendance_data, holidays, lectures = prepare_execution_data(
            schedule_df,
            start_date,
            end_date,
            holiday_text,
            file,
        )

        # ==================================================
        # PREFETCH LMS DATA
        # ==================================================

        course_id = bot.extract_course_id(
            selected_course["url"]
        )

        cached = course_data_cache[course_id]

        student_ids = cached["student_ids"]
        detailed_sessions = cached["sessions"]

        log_message("✅ Using synchronized LMS data.")
        log_message(
            f"✅ Course cache created "
            f"({len(detailed_sessions)} attendance sessions)"
        )

        # ==================================================
        # BUILD CURRENT LECTURE STATUS
        # ==================================================

        excel_dates = set(attendance_data.keys())

        lectures, stats, ready_upload_lectures = analyze_lecture_status(
            lectures,
            detailed_sessions,
            excel_dates,
        )

        log_message(
            f"📚 Planned lectures       : {stats['total_lectures']}"
        )

        log_message(
            f"📝 Already marked on LMS  : {stats['already_marked']}"
        )

        log_message(
            f"📤 Ready for upload       : {stats['ready_upload']}"
        )

        log_message(
            f"⚠️ Missing Excel data     : {stats['missing']}"
        )

        # ==================================================
        # CHECK WHETHER UPLOAD IS REQUIRED
        # ==================================================

        if not ready_upload_lectures:

            log_message("=" * 60)
            log_message("ℹ️ NO NEW ATTENDANCE TO UPLOAD")
            log_message("=" * 60)

            log_message(
                f"📚 Planned Lectures      : "
                f"{stats['total_lectures']}"
            )

            log_message(
                f"📝 Already Marked on LMS : "
                f"{stats['already_marked']}"
            )

            log_message(
                f"⚠️ Missing Excel Data    : "
                f"{stats['missing']}"
            )

            log_message(
                "📤 Ready for Upload      : 0"
            )

            log_message("=" * 60)
            log_message(
                "✅ No new attendance found. "
                "Nothing was uploaded."
            )
            log_message("=" * 60)

            return (
                "ℹ️ No new attendance found. "
                "Nothing was uploaded."
            )

        # ==================================================
        # NAVIGATE
        # ==================================================

        navigate_to_attendance_activity(
            bot,
            selected_course,
        )

        # ==================================================
        # SUMMARY
        # ==================================================

        log_execution_summary(
            selected_course,
            lectures,
            student_ids,
            {
                (session["date"], session["time"])
                for session in detailed_sessions
            },
        )

        # ==================================================
        # AUTOMATION LOOP
        # ==================================================

        (
            executed,
            total,
        ) = execute_automation_loop(
            bot=bot,
            lectures=ready_upload_lectures,
            attendance_data=attendance_data,
        )
        # ==================================================
        # FINAL SUMMARY
        # ==================================================

        log_completion_summary(
            executed,
            total,
        )

        return "✅ Automation completed successfully."

    except Exception as e:

        AppLogger.get_logger().exception(e)

        message = handle_application_error(e)

        log_message(message)

        return message

    finally:

        is_running = False

        log_message("🧹 Cleaning up resources...")

        if bot is not None:

            try:

                bot.close()

                AppLogger.get_logger().info(
                    "Browser closed successfully."
                )

                log_message("✅ Browser closed.")

            except Exception as e:

                AppLogger.get_logger().exception(e)

                log_message(
                    "⚠️ Browser could not be closed cleanly."
                )

        # Drop the reference to the now-closed driver so a
        # stale bot_instance can't be reused by a future call
        # (e.g. get_course_id / on_course_change) before the
        # next successful login repopulates it.
        if bot_instance is bot:
            bot_instance = None

        log_message("🏁 Automation session finished.")

# =========================
# 🎨 PROFESSIONAL THEME SYSTEM
# =========================
import base64
from app_info import (
    APP_NAME,
    VERSION,
    RELEASE_NAME,
    DEVELOPER,
    COPYRIGHT,
    WINDOW_TITLE,
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def logo_base64(path):
    """
    Load an image and return its Base64 representation.
    """

    try:

        with open(path, "rb") as img_file:
            return base64.b64encode(
                img_file.read()
            ).decode("utf-8")

    except FileNotFoundError:

        AppLogger.get_logger().exception(
            "Logo file not found."
        )

    except Exception as e:

        AppLogger.get_logger().exception(e)

    return ""

def save_course_settings(course_name, schedule_df, start_date, end_date, holiday_text):

    if not course_name:
        return "❌ Please select a course."

    settings = {
        "start_date": start_date,
        "end_date": end_date,
        "holidays": parse_holidays(holiday_text),
        "schedule": schedule_df.to_dict("records")
    }

    CourseSettings.save(course_name, settings)

    log_message(f"💾 Settings saved for: {course_name}")

    return "✅ Course settings saved successfully."

# ==========================================================
# 🚀 MAIN APPLICATION
# ==========================================================

with gr.Blocks(
    title="Attendance Automation (Local)"
) as app:

    # ==========================================================
    # SCREEN 1 — AUTHENTICATION
    # ==========================================================

    logo_data = logo_base64(
        PathManager.asset("uaf_logo.png")
    )
    auth_logo_data = logo_base64(
        PathManager.asset("logo_text.png")
    )

    with gr.Column(
        elem_classes=["screen-host"]
    ):

        # ======================================================
        # SCREEN 1 — AUTHENTICATION
        # ======================================================

        (
            authentication_screen,
            auth_username,
            auth_password,
            auth_remember_me,
            login_button,
            authentication_status,
        ) = create_authentication_screen(
            saved_username=saved_username,
            saved_password=saved_password,
            remember_default=remember_default,
            logo_data=auth_logo_data,
        )

        # ======================================================
        # SCREEN 2 — DASHBOARD
        # ======================================================

        dashboard_screen = create_dashboard_screen()

        with dashboard_screen:

            # ======================================================
            # HEADER
            # ======================================================

            with gr.Column(elem_classes=["app-header"]):

                with gr.Row(elem_classes=["header-content"]):

                    gr.HTML(
                        f"""
                        <div class="header-brand">
                            <div class="header-logo">
                                <img
                                    src="data:image/png;base64,{logo_data}"
                                >
                            </div>
                            <div class="header-brand-text">
                                <div class="header-title">
                                    University of Agriculture Faisalabad
                                </div>
                                <div class="header-app-name">
                                    {APP_NAME}
                                </div>
                                <div class="header-subtitle">
                                    Real-time LMS attendance automation system
                                </div>
                            </div>
                        </div>
                        """,
                        elem_classes=["header-brand-wrap"],
                    )

                    with gr.Row(elem_classes=["header-right"]):

                        gr.HTML(
                            """
                            <div class="header-badge">
                                <span class="status-dot"></span>
                                <span>System Ready</span>
                            </div>
                            """
                        )

                        signout_btn = gr.Button(
                            "🚪 Sign Out",
                            elem_classes=["header-btn", "header-btn-neutral"],
                        )

                        exit_btn = gr.Button(
                            "⏻ Exit",
                            elem_classes=["header-btn", "header-btn-danger"],
                        )

            with gr.Row(
                visible=False,
                elem_classes=["exit-confirm-panel"],
            ) as exit_confirm_row:

                gr.HTML(
                    '<span class="exit-confirm-text">'
                    '⚠️ This will close the app and end any running automation. '
                    'Continue?</span>'
                )

                with gr.Row():
                    cancel_exit_btn = secondary_button(
                        "Cancel",
                        elem_classes=["pro-btn"],
                    )
                    confirm_exit_btn = gr.Button(
                        "Yes, Exit",
                        variant="stop",
                        elem_classes=["pro-btn", "pro-btn-danger"],
                    )

            # ======================================================
            # DASHBOARD LAYOUT
            # ======================================================

            with gr.Row(
                elem_classes=["dashboard-layout"]
            ):

                # ==================================================
                # LEFT — MAIN DASHBOARD
                # ==================================================

                with gr.Column(
                    scale=3,
                    elem_classes=["dashboard-main"]
                ):

                    # ==============================================
                    # COURSE DASHBOARD
                    # ==============================================

                    with section_card(
                        "Course Dashboard",
                        "📚",
                        description="Select a course to view and manage its details",
                    ):
                        with section_body():

                            with field_group(
                                "Select Course",
                                "🎓",
                                description="Choose the course you want to manage",
                            ):

                                course_dropdown = app_dropdown(
                                    label="Select Course",
                                    show_label=False,
                                    choices=[],
                                    value=None,
                                    interactive=True,
                                )

                    # ==============================================
                    # ATTENDANCE RECORDS
                    # ==============================================

                    with section_card(
                        "Attendance Records",
                        "📊",
                        description="Review attendance sessions already recorded in the LMS",
                    ):
                        with section_body():

                            marked_output = output_box(
                                label="Already Marked Attendance",
                                lines=8,
                            )

                    # ==============================================
                    # WEEKLY SCHEDULE
                    # ==============================================

                    def get_empty_schedule():

                        return pd.DataFrame({
                            "Day": [
                                "Monday",
                                "Tuesday",
                                "Wednesday",
                                "Thursday",
                                "Friday",
                            ],

                            "Start Time": [
                                "09:00"
                            ] * 5,

                            "Lecture Type": [
                                "Theory"
                            ] * 5,

                            "No. of Lectures": [
                                1
                            ] * 5,

                            "Duration (min)": [
                                50
                            ] * 5,
                        })

                    with section_card(
                        "Weekly Schedule",
                        "📅",
                        description="Define the weekly lecture schedule for this course",
                    ):
                        with section_body():

                            schedule_input = app_dataframe(
                                value=get_empty_schedule(),

                                headers=[
                                    "Day",
                                    "Start Time",
                                    "Lecture Type",
                                    "No. of Lectures",
                                    "Duration (min)",
                                ],

                                datatype=[
                                    "str",
                                    "str",
                                    "str",
                                    "number",
                                    "number",
                                ],

                                row_count=5,

                                column_count=(
                                    5,
                                    "fixed"
                                ),

                                interactive=True,
                            )

                    # ==============================================
                    # ACADEMIC SEMESTER
                    # ==============================================

                    with section_card(
                        "Academic Semester",
                        "📆",
                        description="Set the semester dates used to generate the lecture plan",
                    ):
                        with section_body():

                            with gr.Row():

                                start_date = app_textbox(
                                    label="Semester Start Date *",
                                    placeholder=(
                                        "YYYY-MM-DD "
                                        "(e.g. 2026-02-09)"
                                    ),
                                )

                                end_date = app_textbox(
                                    label="Semester End Date *",
                                    placeholder=(
                                        "YYYY-MM-DD "
                                        "(e.g. 2026-05-29)"
                                    ),
                                )

                            gr.Markdown(
                                """
                                **Lecture Generation Rules**

                                The system will automatically generate
                                all expected lectures between the Semester
                                Start Date and Semester End Date using the
                                Weekly Schedule below. Any holidays
                                specified later will be excluded.
                                """
                            )

                    # ==============================================
                    # HOLIDAYS & UPLOADS
                    # ==============================================

                    with section_card(
                        "Holidays & Uploads",
                        "🏖️",
                        description="Configure holidays and upload the attendance workbook",
                    ):
                        with section_body():

                            holiday_text = app_textbox(
                                label="Holidays (comma-separated dates)",
                                placeholder=(
                                    "YYYY-MM-DD, YYYY-MM-DD"
                                ),
                            )

                            attendance_file = upload_box(
                                label="Upload Attendance Excel",
                            )

                    # ==============================================
                    # SCHEDULE PREVIEW
                    # ==============================================

                    with section_card(
                        "Schedule Preview",
                        "🔍",
                        description="Review the generated lecture schedule before automation",
                    ):
                        with section_body():

                            preview_btn = primary_button(
                                "Preview Schedule"
                            )

                            preview_output = output_box(
                                label="Generated Lectures Schedule",
                                lines=15,
                            )

                    # ==============================================
                    # ACTION BAR
                    # ==============================================

                    with gr.Row():

                        with gr.Column(
                            scale=2
                        ):

                            confirm = app_checkbox(
                                label=(
                                    "I confirm the preview is correct "
                                    "and want to proceed"
                                )
                            )

                        with gr.Column(
                            scale=1
                        ):

                            run_btn = primary_button(
                                "🚀 Run Automation"
                            )

                    # ==============================================
                    # EXECUTION STATUS
                    # ==============================================

                    output = output_box(
                        label="Execution Status",
                        lines=5,
                    )

                # ==================================================
                # RIGHT — LIVE EXECUTION MONITOR
                # ==================================================

                with gr.Column(
                    scale=1,
                    elem_classes=["dashboard-sidebar"]
                ):

                    with section_card(
                        "Live Execution Monitor",
                        "📡",
                        description="Monitor the automation process in real time",
                        elem_classes=["sticky-logs"],
                    ):
                        with section_body():

                            logs_state = gr.State("")

                            authenticated_username = gr.State("")

                            authenticated_password = gr.State("")

                            live_logs = output_box(
                                label="Real-time Logs",
                                lines=25,
                                elem_classes=[
                                    "logs-panel"
                                ],
                            )

                            # Timer starts inactive — it's only
                            # switched on once automation actually
                            # begins (see run_automation_ui below),
                            # instead of polling every 500ms for the
                            # entire lifetime of the session.
                            log_timer = gr.Timer(
                                0.5,
                                active=True,
                            )

            # ======================================================
            # FOOTER
            # ======================================================

            gr.HTML(
                app_footer(
                    app_name=APP_NAME,
                    version=VERSION,
                    developer=DEVELOPER,
                    copyright_text=COPYRIGHT,
                )
            )
#=============================================

    def authenticate_and_show_dashboard(username, password, remember_me):

        log_message(
            f"🔐 Authentication attempt for username: {username}"
        )

        log_message(
            f"🔐 Remember Me: {remember_me}"
        )

        course_names, status, marked_text = load_courses(
            username,
            password,
            remember_me,
        )

        # The login button is always re-enabled here, on both
        # the success and failure paths — previously it stayed
        # stuck on "⏳ Signing in..." / disabled forever after a
        # failed login attempt.
        reset_login_button = gr.update(
            value="Login",
            interactive=True,
        )

        if course_names:
            return (
                gr.update(visible=False),
                gr.update(visible=True),
                status,
                gr.update(
                    choices=course_names,
                    value=None,
                ),
                username,
                password,
                reset_login_button,
            )

        return (
            gr.update(visible=True),
            gr.update(visible=False),
            status,
            gr.update(choices=[]),
            "",
            "",
            reset_login_button,
        )

    
    def show_login_processing():
        return (
            gr.update(
                value="⏳ Signing in...",
                interactive=False,
            ),
            "🔐 Connecting to LMS... Please wait.",
        )

    # =========================
    # SIGN OUT
    # =========================

    def sign_out():
        global bot_instance, courses_list, course_data_cache, is_running

        log_message("🚪 Signing out...")

        if bot_instance is not None:
            try:
                bot_instance.close()
                log_message("✅ Browser closed.")
            except Exception as e:
                AppLogger.get_logger().exception(e)
                log_message("⚠️ Browser could not be closed cleanly.")
            bot_instance = None

        courses_list = []
        course_data_cache = {}
        is_running = False

        log_message("✅ Signed out successfully.")

        return (
            gr.update(visible=True),    # authentication_screen
            gr.update(visible=False),   # dashboard_screen
            "",                          # authentication_status
            gr.update(choices=[], value=None),  # course_dropdown
            "",  # authenticated_username
            "",  # authenticated_password
        )

    # =========================
    # EXIT APP
    # =========================

    def show_exit_confirm():
        return gr.update(visible=True)

    def hide_exit_confirm():
        return gr.update(visible=False)

    def confirm_exit():
        global bot_instance

        log_message("⏻ Exiting application...")

        if bot_instance is not None:
            try:
                bot_instance.close()
                log_message("✅ Browser closed.")
            except Exception as e:
                AppLogger.get_logger().exception(e)
                log_message("⚠️ Browser could not be closed cleanly.")
            bot_instance = None

        log_message("👋 Goodbye.")

        # Give the UI a moment to flush the final log line to the
        # client before the process is torn down.
        threading.Timer(1.0, lambda: os._exit(0)).start()

        return gr.update(visible=False)
    # =========================
    # EVENT HANDLERS
    # =========================
    signout_btn.click(
        fn=sign_out,
        inputs=[],
        outputs=[
            authentication_screen,
            dashboard_screen,
            authentication_status,
            course_dropdown,
            authenticated_username,
            authenticated_password,
        ],
        show_progress="hidden",
    )

    exit_btn.click(
        fn=show_exit_confirm,
        outputs=[exit_confirm_row],
        show_progress="hidden",
    )

    cancel_exit_btn.click(
        fn=hide_exit_confirm,
        outputs=[exit_confirm_row],
        show_progress="hidden",
    )

    confirm_exit_btn.click(
        fn=confirm_exit,
        outputs=[exit_confirm_row],
        show_progress="hidden",
    )

    login_button.click(
        fn=show_login_processing,
        inputs=[],
        outputs=[
            login_button,
            authentication_status,
        ],
        show_progress="hidden",
    ).then(
        fn=authenticate_and_show_dashboard,
        inputs=[
            auth_username,
            auth_password,
            auth_remember_me,
        ],
        outputs=[
            authentication_screen,
            dashboard_screen,
            authentication_status,
            course_dropdown,
            authenticated_username,
            authenticated_password,
            login_button,
        ],
        show_progress="hidden",
    )

    # Course change handler
    course_dropdown.change(
        on_course_change,
        inputs=[course_dropdown],
        outputs=[
            marked_output,
            schedule_input,
            start_date,
            end_date,
            holiday_text,
            attendance_file,
            preview_output,
            confirm,
            output,
            logs_state,
            live_logs,
        ]
    )

    # Preview handler
    preview_btn.click(
        preview_schedule,
        inputs=[
            schedule_input,
            start_date,
            end_date,
            holiday_text,
            attendance_file,
            course_dropdown
        ],
        outputs=preview_output
    )


    def control_timer():
        """
        Keep the Live Execution Monitor timer running only
        while automation is actually active. Called on every
        tick so the timer switches itself off as soon as
        `run_automation` finishes (its `finally` block sets
        `is_running = False`), instead of polling forever.
        """
        if is_running:
            return gr.Timer(active=True)
        return gr.Timer(active=False)

    # =========================
    # LIVE STREAMING LOGIC (GRADIO 6.12.0)
    # =========================
    
    def update_logs_stream(current_logs):
        """Called by gr.Timer every 500ms to fetch new logs"""
        new_logs = get_logs_from_queue()
        if new_logs:
            current_logs += "\n".join(new_logs) + "\n"
            # Keep last 200 lines to prevent memory bloat
            lines = current_logs.split("\n")
            if len(lines) > 200:
                current_logs = "\n".join(lines[-200:])
        return current_logs
    
    
    
    # When timer ticks: read queue, update state, update display,
    # then decide whether the timer should keep running.
    log_timer.tick(
        update_logs_stream,
        inputs=[logs_state],
        outputs=[logs_state]
    ).then(
        lambda x: x,
        inputs=[logs_state],
        outputs=[live_logs]
    )
    #.then(
    #    control_timer,
    #    inputs=[],
    #    outputs=[log_timer],
    #)

    
    # =========================
    # RUN AUTOMATION WITH STREAMING
    # =========================
    
    def run_automation_ui(schedule_df, start_date, end_date, holiday_text, file, course, confirm, username, password):

        import threading
        global is_running

        if is_running:
            return "⚠️ Automation already running!", "", gr.Timer(active=True)

        is_running = True
        
        # Clear logs
        while not log_queue.empty():
            log_queue.get()

        def run_main():
            run_automation(
                schedule_df, start_date, end_date, holiday_text, file,
                course, confirm, username, password
            )

        # ✅ Start correctly
        threading.Thread(target=run_main, daemon=True).start()

        # Switch the log timer on now that automation has
        # actually started; it will switch itself back off
        # (via control_timer) once run_automation's `finally`
        # block flips is_running back to False.
        return (
            "🚀 Automation started... Check live logs.",
            "",
            gr.Timer(active=True),
        )

    run_btn.click(
        run_automation_ui,
        inputs=[
            schedule_input, start_date, end_date, holiday_text, attendance_file,
            course_dropdown, confirm, authenticated_username, authenticated_password
        ],
        outputs=[output, logs_state, log_timer]
    ).then(
        lambda x: x,  # Display final logs
        inputs=[logs_state],
        outputs=[live_logs]
    )

app.queue()
# =========================
# 🚀 LAUNCH
# =========================

def launch_app():
    app.queue()
    return app.launch(
        server_name="127.0.0.1",
        server_port=7860,
        share=False,
        favicon_path=PathManager.asset("wizard_small.bmp"),
        css=custom_css,
        theme=gr.themes.Soft(
            primary_hue="emerald",
            secondary_hue="slate",
            neutral_hue="slate",
            font=gr.themes.GoogleFont("Inter"),
            font_mono=gr.themes.GoogleFont("JetBrains Mono"),
        ).set(
            body_background_fill="*neutral_50",
            block_background_fill="*neutral_50",
            block_border_width="0px",
            block_label_background_fill="*primary_50",
            block_label_text_color="*primary_700",
            block_title_text_color="*primary_700",
            input_background_fill="*neutral_100",
            button_primary_background_fill="*primary_600",
            button_primary_background_fill_hover="*primary_700",
            button_secondary_background_fill="*neutral_100",
            button_secondary_background_fill_hover="*primary_50",
            button_secondary_text_color="*neutral_700",
        )
    )
