"""Application configuration.

Configuration is environment-driven: environment-specific values are read
from environment variables (or a local .env file) so that no secret is
ever committed to source control.

Author: Charon (Technical Lead)
"""
import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env if present (local development only; never loaded in production).
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


class BaseConfig:
    """Settings shared by every environment."""

    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-me")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{BASE_DIR / 'instance' / 'redgum.sqlite3'}"
    )
    # Timetable window
    TIMETABLE_START_HOUR = int(os.environ.get("TIMETABLE_START_HOUR", "9"))
    TIMETABLE_END_HOUR = int(os.environ.get("TIMETABLE_END_HOUR", "20"))


class DevelopmentConfig(BaseConfig):
    DEBUG = True


class TestingConfig(BaseConfig):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"


class ProductionConfig(BaseConfig):
    DEBUG = False

    @classmethod
    def init_app(cls, app):
        # Fail fast in production if no secret is provided.
        if not app.config.get("SECRET_KEY") or app.config["SECRET_KEY"] == "dev-secret-change-me":
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
