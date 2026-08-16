"""
=========================================================
Course Settings Manager
LMS Attendance Automation System
Version 8.1
=========================================================
"""

import json
from typing import Optional

from path_manager import PathManager


class CourseSettings:
    """
    Handles saving and loading settings for individual LMS courses.

    Storage:

        UserData/
            courses/
                <course_id>.json
    """

    # --------------------------------------------------
    # Helpers
    # --------------------------------------------------

    @staticmethod
    def _ensure_folder():
        """
        Create the courses directory if it doesn't exist.
        """
        PathManager.COURSES_DIR.mkdir(
            parents=True,
            exist_ok=True
        )

    @classmethod
    def _directory(cls):
        """
        Returns the courses storage directory.
        """
        cls._ensure_folder()
        return PathManager.COURSES_DIR

    @classmethod
    def _file_path(cls, course_id: str):
        """
        Returns the JSON file path for a course.
        """
        return cls._directory() / f"{course_id}.json"

    # --------------------------------------------------
    # Save
    # --------------------------------------------------

    @classmethod
    def save(cls, course_id: str, settings: dict) -> bool:
        """
        Save settings for a course.

        Returns:
            True if successful.
        """

        file_path = cls._file_path(course_id)

        with file_path.open(
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                settings,
                f,
                indent=4,
                ensure_ascii=False
            )

        return True

    # --------------------------------------------------
    # Load
    # --------------------------------------------------

    @classmethod
    def load(cls, course_id: str) -> Optional[dict]:
        """
        Load saved settings.

        Returns:
            dict if found,
            None otherwise.
        """

        file_path = cls._file_path(course_id)

        if not file_path.exists():
            return None

        try:

            with file_path.open(
                "r",
                encoding="utf-8"
            ) as f:

                return json.load(f)

        except Exception:
            # Corrupted JSON
            return None

    # --------------------------------------------------
    # Exists
    # --------------------------------------------------

    @classmethod
    def exists(cls, course_id: str) -> bool:
        """
        Returns True if settings exist.
        """

        return cls._file_path(course_id).exists()

    # --------------------------------------------------
    # Delete
    # --------------------------------------------------

    @classmethod
    def delete(cls, course_id: str) -> bool:
        """
        Delete saved settings.

        Returns:
            True if deleted.
            False if file not found.
        """

        file_path = cls._file_path(course_id)

        if file_path.exists():
            file_path.unlink()
            return True

        return False

    # --------------------------------------------------
    # List
    # --------------------------------------------------

    @classmethod
    def list_saved_courses(cls):
        """
        Returns a sorted list of all saved course IDs.
        """

        cls._ensure_folder()

        files = PathManager.COURSES_DIR.glob("*.json")

        return sorted(
            f.stem
            for f in files
        )