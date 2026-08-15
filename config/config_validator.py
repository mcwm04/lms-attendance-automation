"""
=========================================================
Configuration Validator
LMS Attendance Automation System
Version 8
=========================================================
"""

from exceptions import ConfigurationValidationError


class ConfigValidator:
    """Validates application configuration."""

    REQUIRED_SECTIONS = (
        "application",
        "browser",
        "logging",
        "lms",
        "ui",
    )

    @classmethod
    def validate(cls, config):
        """
        Validate complete configuration.
        """

        cls.validate_required_sections(config)

        return True

    @classmethod
    def validate_required_sections(cls, config):
        """
        Validate required top-level sections.
        """

        errors = []

        for section in cls.REQUIRED_SECTIONS:

            if section not in config:
                errors.append(
                    f"Missing required configuration section: {section}"
                )

        if errors:
            raise ConfigurationValidationError(
                "\n".join(errors)
            )

        return True