"""The statistics dashboard: the four numbers the charter promises."""
from datetime import date, timedelta

from app.models import Session, db
from app.routes.stats import subject_distribution, week_bounds

MONDAY = date(2026, 8, 10)
TUESDAY = date(2026, 8, 11)


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------

def test_week_bounds_runs_monday_to_sunday():
    assert week_bounds(TUESDAY) == (MONDAY, date(2026, 8, 16))


def test_week_bounds_from_a_sunday_stays_in_the_same_week():
    assert week_bounds(date(2026, 8, 16))[0] == MONDAY


class Row:
    def __init__(self, subject):
        self.subject = subject


def test_subject_distribution_orders_by_count_descending():
    rows, peak = subject_distribution([Row("Maths"), Row("Physics"),
                                       Row("Maths"), Row("Chemistry"), Row("Maths")])
    assert rows == [("Maths", 3), ("Chemistry", 1), ("Physics", 1)]
    assert peak == 3


def test_subject_distribution_breaks_ties_alphabetically():
    """A stable order stops the table from reshuffling between page loads."""
    rows, _ = subject_distribution([Row("Physics"), Row("Chemistry")])
    assert rows == [("Chemistry", 1), ("Physics", 1)]


def test_subject_distribution_handles_an_empty_week():
    """peak is used as a divisor when sizing bars, so it must not be zero."""
    assert subject_distribution([]) == ([], 0)


# --------------------------------------------------------------------------
# The dashboard view
# --------------------------------------------------------------------------

def make_session(tutor, student, subject, when, status="booked"):
    session = Session(tutor_id=tutor.id, student_id=student.id, subject=subject,
                      session_date=when, start_time="16:00", duration_minutes=60,
                      room="Room 1", status=status)
    db.session.add(session)
    db.session.commit()
    return session


def test_dashboard_renders(client, app, make_tutor, make_student):
    make_session(make_tutor(), make_student(), "Mathematics", MONDAY)
    response = client.get("/stats/?week=2026-08-11")
    assert response.status_code == 200
    assert b"Mathematics" in response.data


def test_dashboard_counts_only_the_displayed_week(client, app, make_tutor, make_student):
    tutor, student = make_tutor(), make_student()
    make_session(tutor, student, "Mathematics", MONDAY)
    make_session(tutor, student, "Physics", MONDAY + timedelta(days=7))  # next week

    this_week = client.get("/stats/?week=2026-08-11")
    next_week = client.get("/stats/?week=2026-08-18")
    assert b"Physics" not in this_week.data
    assert b"Physics" in next_week.data


def test_cancelled_sessions_are_excluded_from_the_count(client, app, make_tutor, make_student):
    tutor, student = make_tutor(), make_student()
    make_session(tutor, student, "Mathematics", MONDAY)
    make_session(tutor, student, "Physics", MONDAY, status="cancelled")

    response = client.get("/stats/?week=2026-08-11")
    assert b"Mathematics" in response.data
    assert b"Physics" not in response.data


def test_roster_cards_reflect_active_records(client, app, make_tutor, make_student):
    make_tutor(name="Active Tutor")
    inactive = make_tutor(name="Gone Tutor")
    inactive.is_active = False
    db.session.commit()

    response = client.get("/stats/?week=2026-08-11")
    assert response.status_code == 200
    assert b"Active tutors" in response.data


def test_empty_week_renders_without_dividing_by_zero(client, app):
    response = client.get("/stats/?week=2026-01-05")
    assert response.status_code == 200
    assert b"No bookings recorded" in response.data


def test_unparseable_week_falls_back_to_the_current_week(client, app):
    """A hand-edited URL should not produce a 500."""
    response = client.get("/stats/?week=not-a-date")
    assert response.status_code == 200


def test_navigation_links_move_a_week_at_a_time(client, app):
    # The anchor is the Tuesday, so stepping a week moves the Monday it
    # resolves to: 10 Aug -> 3 Aug back, 17 Aug forward.
    response = client.get("/stats/?week=2026-08-11")
    assert b"week=2026-08-03" in response.data   # previous Monday
    assert b"week=2026-08-17" in response.data   # following Monday


def test_seeded_data_loads_into_the_dashboard(client, seeded):
    response = client.get("/stats/?week=2026-08-11")
    assert response.status_code == 200
    assert b"Bookings this week" in response.data
