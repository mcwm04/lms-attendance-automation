# LMS Attendance Automation System

A Windows desktop application that automates attendance submission to the
University of Agriculture Faisalabad's Learning Management System
([lms.uaf.edu.pk](https://lms.uaf.edu.pk)) — built for faculty who currently
mark attendance by hand, session by session, on the LMS website.

Given a weekly lecture schedule and an attendance workbook (Excel), it logs
into the LMS, opens each course's attendance activity, and marks
Present/Absent/Leave for every student automatically — skipping any session
that's already been marked, so it's safe to run repeatedly throughout a
semester.

## Features

- 🔐 **Secure credential storage** — LMS username/password encrypted at rest
  (Fernet) with hardened file permissions; "Remember Me" is optional
- 📅 **Automatic lecture planning** — generates the semester's expected
  lectures from a weekly schedule, semester dates, and a holiday list
- 🔄 **LMS synchronization** — checks what's already marked on the LMS before
  uploading anything, so nothing gets submitted twice
- 📊 **Attendance sync report** — a clear before-you-run preview of what's
  already marked, what's ready to upload, and what's missing from your Excel
  file
- 📡 **Live execution monitor** — real-time log streaming while automation
  runs, so you can watch progress lecture by lecture
- 🖥️ **Desktop app** — packaged as a standalone Windows application (Gradio
  UI inside a native window via pywebview), with a professional installer

## Screenshots

*(add screenshots of the login screen and dashboard here)*

## Requirements (for running the installed app)

- Windows 10 or 11
- Google Chrome or Microsoft Edge installed
- An LMS account at lms.uaf.edu.pk

## Installation

1. Download the latest installer from the [Releases](../../releases) page
2. Run `LMSAttendanceAutomation_Setup_x.x.x.exe`
3. Accept the license agreement and follow the wizard
   (installs to `%LocalAppData%\LMS Attendance Automation System` — no admin
   rights required)
4. Launch from the Start Menu or desktop shortcut

## Usage

1. Sign in with your LMS username and password
2. Select a course from the dropdown
3. Fill in the weekly schedule (day, start time, lecture type, duration)
4. Set the semester start/end dates and any holidays
5. Upload the attendance Excel workbook (see `AttendanceSample.xlsx` for the
   expected format)
6. Click **Preview Schedule** to review what will be uploaded
7. Confirm the preview and click **Run Automation**

## Tech Stack

| Layer | Technology |
|---|---|
| UI | [Gradio](https://gradio.app) inside a native window via [pywebview](https://pywebview.flowrl.com) |
| Browser automation | [Selenium](https://www.selenium.dev) + [webdriver-manager](https://pypi.org/project/webdriver-manager/) |
| Credential encryption | [cryptography](https://cryptography.io) (Fernet) |
| Data handling | pandas + openpyxl |
| Packaging | [PyInstaller](https://pyinstaller.org) |
| Installer | [Inno Setup](https://jrsoftware.org/isinfo.php) |

## Building From Source

```bash
# clone the repo
git clone https://github.com/YOUR-USERNAME/lms-attendance-automation.git
cd lms-attendance-automation

# install dependencies
pip install -r requirements.txt

# run directly
python desktop.py
```

## Building the Installer

```bash
# regenerate the Windows version resource
python generate_version_file.py

# build the standalone executable
pyinstaller desktop.spec

# compile the installer (requires Inno Setup 6)
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" setup.iss
```

The compiled installer will be written to `installer\`.

## Project Structure

```
├── app.py                  # Main Gradio application & UI wiring
├── desktop.py               # Desktop launcher (pywebview window)
├── automator.py              # Selenium automation logic
├── browser_manager.py        # Chrome/Edge driver setup
├── credential_manager.py     # Encrypted credential storage
├── course_settings.py        # Per-course schedule persistence
├── bootstrap.py               # App startup / folder initialization
├── config/                    # Configuration management
├── ui/                         # Reusable UI components & widgets
├── assets/                     # Icons, images, stylesheet
├── setup.iss                   # Inno Setup installer script
└── desktop.spec                # PyInstaller build spec
```

## Configuration

Runtime configuration lives in `UserData\config.json` (created on first run
from `config\defaults.json`). Key settings:

| Section | Key | Description |
|---|---|---|
| `browser` | `headless` | Run the automation browser invisibly |
| `browser` | `timeout` | Selenium wait timeout (seconds) |
| `lms` | `url` | Base LMS URL |

## Security Notes

- Credentials are encrypted locally with a per-installation Fernet key and
  are never transmitted anywhere except directly to the LMS login form
- The application ignores SSL certificate warnings when connecting to the
  LMS due to a known certificate issue on `lms.uaf.edu.pk` — be aware this
  disables certificate validation for the automation browser session

## License

See [LICENSE.txt](LICENSE.txt).

## Author

**Waqas Ahmad**
