import base64
import json
from pathlib import Path

from cryptography.fernet import Fernet

from path_manager import PathManager


class CredentialManager:
    """
    Secure storage for LMS credentials.
    """

    KEY_FILE = PathManager.USER_DATA_DIR / "credentials.key"
    DATA_FILE = PathManager.USER_DATA_DIR / "credentials.dat"

    @classmethod
    def _load_key(cls):
        if cls.KEY_FILE.exists():
            return cls.KEY_FILE.read_bytes()

        key = Fernet.generate_key()
        cls.KEY_FILE.write_bytes(key)
        return key

    @classmethod
    def _cipher(cls):
        return Fernet(cls._load_key())

    @classmethod
    def save(cls, username, password):
        data = {
            "username": username,
            "password": password
        }

        encrypted = cls._cipher().encrypt(
            json.dumps(data).encode("utf-8")
        )

        cls.DATA_FILE.write_bytes(encrypted)

    @classmethod
    def load(cls):
        if not cls.DATA_FILE.exists():
            return "", ""

        try:
            decrypted = cls._cipher().decrypt(
                cls.DATA_FILE.read_bytes()
            )

            data = json.loads(
                decrypted.decode("utf-8")
            )

            return (
                data.get("username", ""),
                data.get("password", "")
            )

        except Exception:
            return "", ""

    @classmethod
    def clear(cls):
        if cls.DATA_FILE.exists():
            cls.DATA_FILE.unlink()