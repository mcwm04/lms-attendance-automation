"""
=========================================================
Configuration Manager
LMS Attendance Automation System
Version 8
=========================================================
"""

import json
from config.config_migrator import ConfigMigrator
from path_manager import PathManager
from exceptions import *


class ConfigManager:

    _config = None

    @classmethod
    def _load_defaults(self):
        """
        Load the bundled default configuration.

        Raises:
            ConfigurationError:
                If the bundled configuration cannot be loaded.
        """

        defaults_path = PathManager.config("defaults.json")

        try:
            with defaults_path.open("r", encoding="utf-8") as f:
                return json.load(f)

        except FileNotFoundError as exc:
            raise ConfigurationError(
                f"Bundled configuration file not found: {defaults_path}"
            ) from exc

        except json.JSONDecodeError as exc:
            raise ConfigurationError(
                f"Bundled configuration is not valid JSON: {defaults_path}"
            ) from exc

        except PermissionError as exc:
            raise ConfigurationError(
                f"Permission denied while reading bundled configuration: {defaults_path}"
            ) from exc

        except OSError as exc:
            raise ConfigurationError(
                f"Unable to read bundled configuration: {exc}"
            ) from exc

    @classmethod
    def _load_user_config(cls):
        """
        Load the user configuration.

        Raises:
            ConfigurationError:
                If the user configuration cannot be loaded.
        """

        try:
            with PathManager.user_config().open("r", encoding="utf-8") as file:
                return json.load(file)

        except FileNotFoundError as exc:
            raise ConfigurationError(
                f"User configuration file not found: {PathManager.user_config()}"
            ) from exc

        except json.JSONDecodeError as exc:
            raise ConfigurationError(
                f"User configuration is not valid JSON: {PathManager.user_config()}"
            ) from exc

        except PermissionError as exc:
            raise ConfigurationError(
                f"Permission denied while reading user configuration: {PathManager.user_config()}"
            ) from exc

        except OSError as exc:
            raise ConfigurationError(
                f"Unable to read user configuration: {exc}"
            ) from exc


    @classmethod
    def _save(cls):
        """
        Persist the current user configuration.

        Raises:
            ConfigurationError:
                If the configuration cannot be written.
        """

        try:
            with PathManager.user_config().open(
                "w",
                encoding="utf-8"
            ) as file:

                json.dump(
                    cls._config,
                    file,
                    indent=4,
                    ensure_ascii=False
                )

        except PermissionError as exc:
            raise ConfigurationError(
                "Permission denied while saving the user configuration."
            ) from exc

        except (TypeError, ValueError) as exc:
            raise ConfigurationError(
                "Configuration contains values that cannot be serialized."
            ) from exc

        except OSError as exc:
            raise ConfigurationError(
                f"Unable to save the user configuration: {exc}"
            ) from exc
    
    @classmethod
    def load(cls):
        """Load configuration from disk."""

        if cls._config is None:

            # Load bundled defaults
            defaults = cls._load_defaults()

            # Load user configuration
            user_config = cls._load_user_config()

            # Run migration
            migrated = ConfigMigrator.migrate(defaults, user_config)

            # Save only if changes were made
            if migrated != user_config:
                cls._save(migrated)

            cls._config = migrated

        return cls._config

    @classmethod
    def reload(cls):
        """Force reload from disk."""

        cls._config = None
        return cls.load()

    @classmethod
    def get(cls, *keys, default=None):
        """
        Retrieve nested configuration values.

        If a key is missing:
        - return the supplied default (if provided)
        - otherwise raise ConfigurationKeyError
        """

        data = cls.load()

        path = []

        for key in keys:

            path.append(str(key))

            if not isinstance(data, dict):
                raise ConfigurationKeyError(
                    f"Invalid configuration path: {'.'.join(path)}"
                )

            if key not in data:

                if default is not None:
                    return default

                raise ConfigurationKeyError(
                    f"Missing configuration key: {'.'.join(path)}"
                )

            data = data[key]

        return data

    @classmethod
    def set(cls, section, key, value):
        """Update a configuration value."""

        cls.load()

        cls._config[section][key] = value

        cls._save()