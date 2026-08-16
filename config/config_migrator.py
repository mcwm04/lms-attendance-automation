"""
=========================================================
Configuration Migrator
LMS Attendance Automation System
Version 8
=========================================================
"""

from copy import deepcopy


class ConfigMigrator:
    """Handles configuration schema upgrades."""

    @staticmethod
    def migrate(defaults, user_config):
        """
        Merge defaults into an existing user configuration.
        Existing user values are preserved.
        Missing keys are added.
        """

        migrated = deepcopy(user_config)

        ConfigMigrator._merge(defaults, migrated)

        # Always update schema version
        migrated["_config_version"] = defaults.get("_config_version", 1)

        return migrated

    @staticmethod
    def _merge(defaults, target):
        """Recursively merge missing keys."""

        for key, value in defaults.items():

            if key not in target:
                target[key] = deepcopy(value)

            elif isinstance(value, dict) and isinstance(target[key], dict):
                ConfigMigrator._merge(value, target[key])