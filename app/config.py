"""Application configuration.

Configuration is environment-driven: environment-specific values are read
from environment variables (or a local .env file) so that no secret is
ever committed to source control.

Author: Han (Technical Lead)
"""
import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env if present (local development only; never loaded in production).
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


DEV_SECRET_PLACEHOLDER = "dev-secret-change-me"


class BaseConfig:
    """Settings shared by every environment."""

    SECRET_KEY = os.environ.get("SECRET_KEY", DEV_SECRET_PLACEHOLDER)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{BASE_DIR / 'instance' / 'redgum.sqlite3'}"
    )
    # Timetable window
    TIMETABLE_START_HOUR = int(os.environ.get("TIMETABLE_START_HOUR", "9"))
    TIMETABLE_END_HOUR = int(os.environ.get("TIMETABLE_END_HOUR", "20"))

    @classmethod
    def init_app(cls, app):
        """Validate this environment's settings before the app serves traffic.

        Flask's ``Config.from_object`` copies uppercase attributes onto
        ``app.config`` and nothing more -- it never calls ``init_app``. Unless
        ``create_app`` invokes this explicitly, every guard defined below is
        unreachable.
        """


class DevelopmentConfig(BaseConfig):
    DEBUG = True


class TestingConfig(BaseConfig):
    TESTING = True
    # Use a file-based temp SQLite so the schema persists across connections
    # (in-memory SQLite can reset between connections on Linux CI runners).
    import tempfile
    _db_fd, _db_path = tempfile.mkstemp(suffix=".sqlite3")
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{_db_path}"


class ProductionConfig(BaseConfig):
    DEBUG = False

    @classmethod
    def init_app(cls, app):
        super().init_app(app)
        # Fail fast rather than signing sessions with a value that is public
        # in the repository.
        if app.config.get("SECRET_KEY") in (None, "", DEV_SECRET_PLACEHOLDER):
            raise RuntimeError(
                "SECRET_KEY environment variable must be set in production."
            )


CONFIG_MAP = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}


def get_config(name: str | None = None):
    name = (name or os.environ.get("FLASK_ENV", "development")).lower()
    return CONFIG_MAP.get(name, DevelopmentConfig)
