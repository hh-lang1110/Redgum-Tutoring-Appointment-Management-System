"""Shared pytest fixtures.

Every test runs against a schema rebuilt from the models in a throwaway
SQLite file, so tests cannot leak state into each other or touch the
development database.
"""
import pytest

from app import create_app
from app.models import Student, Tutor, TutorAvailability, db
from app.seed import seed_database


@pytest.fixture
def app():
    application = create_app("testing")
    with application.app_context():
        db.drop_all()
        db.create_all()
        yield application
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def seeded(app):
    """The test app with the demo data from seed.py loaded."""
    seed_database()
    return app


@pytest.fixture
def make_tutor(app):
    """Create a tutor, optionally with availability windows.

    A window is ``(weekday, start, end)`` with weekday 0 == Monday.
    """
    def _make(name="Tomas Ferreira", subjects="Mathematics",
              windows=((0, "15:00", "19:00"),)):
        tutor = Tutor(name=name, subjects=subjects)
        db.session.add(tutor)
        db.session.flush()
        for weekday, start, end in windows or ():
            db.session.add(TutorAvailability(tutor_id=tutor.id, day_of_week=weekday,
                                             start_time=start, end_time=end))
        db.session.commit()
        return tutor
    return _make


@pytest.fixture
def make_student(app):
    """Create a student enrolled in ``subjects``."""
    def _make(name="Ella Nguyen", subjects="Mathematics"):
        student = Student(name=name, enrolled_subjects=subjects)
        db.session.add(student)
        db.session.commit()
        return student
    return _make
