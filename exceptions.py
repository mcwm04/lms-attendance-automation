"""
=========================================================
Custom Exceptions
LMS Attendance Automation System
Version 8
=========================================================
"""


class ApplicationError(Exception):
    """Base class for all application exceptions."""
    pass


# ---------------------------------------------------------
# Browser Exceptions
# ---------------------------------------------------------

class BrowserStartupError(ApplicationError):
    """Raised when no supported browser can be started."""
    pass


# ---------------------------------------------------------
# Configuration Exceptions
# ---------------------------------------------------------

class ConfigurationError(ApplicationError):
    """Base configuration exception."""
    pass


class ConfigurationKeyError(ConfigurationError):
    """Raised when a required configuration key is missing."""
    pass


class ConfigurationValidationError(ConfigurationError):
    """Raised when configuration validation fails."""
    pass


class ConfigurationMigrationError(ConfigurationError):
    """Raised when configuration migration fails."""
    pass

# ---------------------------------------------------------
# Login Exceptions
# ---------------------------------------------------------

class LoginError(ApplicationError):
    """Base class for login related exceptions."""
    pass


class InvalidCredentialsError(LoginError):
    """Raised when username or password is incorrect."""
    pass


class LoginTimeoutError(LoginError):
    """Raised when the login page or login process times out."""
    pass


class LMSUnavailableError(LoginError):
    """Raised when the LMS website cannot be reached."""
    pass

# ---------------------------------------------------------
# Browser Runtime Exceptions
# ---------------------------------------------------------

class BrowserClosedError(ApplicationError):
    """Raised when the browser is closed during automation."""
    pass


class BrowserNavigationError(ApplicationError):
    """Raised when browser navigation fails."""
    pass

# ---------------------------------------------------------
# Course Exceptions
# ---------------------------------------------------------

class CourseLoadError(ApplicationError):
    """Raised when courses cannot be loaded."""
    pass


class CourseSelectionError(ApplicationError):
    """Raised when course selection fails."""
    pass

# ---------------------------------------------------------
# Attendance Exceptions
# ---------------------------------------------------------

class AttendanceError(ApplicationError):
    """Base attendance exception."""
    pass


class AttendanceLoadError(AttendanceError):
    """Raised when attendance sessions cannot be loaded."""
    pass


class AttendanceSubmissionError(AttendanceError):
    """Raised when attendance submission fails."""
    pass

# ---------------------------------------------------------
# Excel Exceptions
# ---------------------------------------------------------

class ExcelValidationError(ApplicationError):
    """Raised when the Excel file is invalid."""
    pass

# ---------------------------------------------------------
# Automation Exceptions
# ---------------------------------------------------------

class AutomationCancelledError(ApplicationError):
    """Raised when automation is cancelled by the user."""
    pass


class AutomationError(ApplicationError):
    """Raised when the attendance automation process fails."""
    pass

class CourseNotFoundError(ApplicationError):
    """Raised when the selected course cannot be found."""
    pass

class LMSAutomationError(Exception):
    """Base exception for all LMS automation errors."""
    pass


class ConfirmationRequiredError(LMSAutomationError):
    """Raised when automation is started without user confirmation."""
    pass


class NoActiveSessionError(LMSAutomationError):
    """Raised when no authenticated Moodle session exists."""
    pass


class ExcelFileRequiredError(LMSAutomationError):
    """Raised when the attendance Excel file is missing."""
    pass


class CourseNotFoundError(LMSAutomationError):
    """Raised when the selected course is not available."""
    pass


class ScheduleValidationError(LMSAutomationError):
    """Raised when the lecture schedule is invalid."""
    pass

class AttendanceLoadError(LMSAutomationError):
    """Raised when attendance information cannot be loaded."""
    pass

class AttendanceSubmissionError(AutomationError):
    """
    Raised when attendance submission to the LMS fails.
    """
    pass