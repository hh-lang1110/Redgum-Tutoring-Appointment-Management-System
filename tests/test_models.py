"""Unit tests for the domain helpers in app/models.py.

These encode the rules the rest of the system assumes: how a time string is
read, what "teaches this subject" means, when a session fits a window, and
when two sessions collide.
"""
from datetime import date

import pytest

from app.models import Session, to_minutes

# --------------------------------------------------------------------------
# to_minutes: every booking rule is built on this parser
# --------------------------------------------------------------------------

@pytest.mark.parametrize("value,expected", [
    ("00:00", 0),
    ("09:30", 570),
    ("15:30", 930),
    ("23:59", 1439),
])
def test_to_minutes_reads_valid_times(value, expected):
    assert to_minutes(value) == expected


@pytest.mark.parametrize("value", [
    "24:00",    # hour out of range
    "12:60",    # minute out of range
    "99:99",
    "-1:00",
    "half past three",
    "",
    None,
    "1230",
])
def test_to_minutes_rejects_invalid_times(value):
    assert to_minutes(value) is None


# --------------------------------------------------------------------------
# Subject matching
# --------------------------------------------------------------------------

def test_teaches_ignores_case_and_padding(make_tutor):
    tutor = make_tutor(subjects="Mathematics, Maths Methods")
    assert tutor.teaches("Mathematics")
    assert tutor.teaches("mathematics")
    assert tutor.teaches("  MATHS METHODS ")


def test_teaches_rejects_other_subjects(make_tutor):
    tutor = make_tutor(subjects="Mathematics")
    assert not tutor.teaches("Chemistry")
    assert not tutor.teaches("")
    assert not tutor.teaches(None)


def test_teaches_does_not_match_partial_words(make_tutor):
    """'Maths' must not satisfy a tutor listed for 'Mathematics'."""
    tutor = make_tutor(subjects="Mathematics")
    assert not tutor.teaches("Maths")


def test_enrolled_in_matches_student_subjects(make_student):
    student = make_student(subjects="Mathematics, Physics")
    assert student.enrolled_in("physics")
    assert not student.enrolled_in("Chemistry")


# --------------------------------------------------------------------------
# Availability: the core rule is that a session fits inside one window
# --------------------------------------------------------------------------

def test_session_inside_window_fits(make_tutor):
    tutor = make_tutor(windows=[(0, "15:00", "19:00")])
    ok, _ = tutor.can_fit(0, "16:00", 60)
    assert ok


def test_session_may_use_the_whole_window(make_tutor):
    tutor = make_tutor(windows=[(0, "15:00", "19:00")])
    assert tutor.can_fit(0, "15:00", 240)[0]


def test_session_before_window_is_rejected(make_tutor):
    tutor = make_tutor(windows=[(0, "15:00", "19:00")])
    ok, reason = tutor.can_fit(0, "14:00", 60)
    assert not ok
    assert "only available" in reason


def test_session_overrunning_window_end_is_rejected(make_tutor):
    """Starting inside the window is not enough; it must finish inside too."""
    tutor = make_tutor(windows=[(0, "15:00", "19:00")])
    assert not tutor.can_fit(0, "18:30", 60)[0]


def test_tutor_without_availability_cannot_be_booked(make_tutor):
    tutor = make_tutor(windows=[])
    ok, reason = tutor.can_fit(0, "16:00", 60)
    assert not ok
    assert "no availability" in reason


def test_availability_is_per_weekday(make_tutor):
    tutor = make_tutor(windows=[(0, "15:00", "19:00")])
    assert tutor.can_fit(0, "16:00", 60)[0]
    assert not tutor.can_fit(1, "16:00", 60)[0]


def test_invalid_start_time_is_reported(make_tutor):
    tutor = make_tutor(windows=[(0, "15:00", "19:00")])
    ok, reason = tutor.can_fit(0, "not a time", 60)
    assert not ok
    assert "Invalid start time" in reason


# --------------------------------------------------------------------------
# Session times
# --------------------------------------------------------------------------

def test_end_time_adds_the_duration(make_tutor, make_student):
    session = Session(tutor_id=make_tutor().id, student_id=make_student().id,
                      subject="Mathematics", session_date=date(2026, 8, 10),
                      start_time="15:30", duration_minutes=90)
    assert session.end_time() == "17:00"


def test_end_time_wraps_past_midnight(make_tutor, make_student):
    session = Session(tutor_id=make_tutor().id, student_id=make_student().id,
                      subject="Mathematics", session_date=date(2026, 8, 10),
                      start_time="23:30", duration_minutes=60)
    assert session.end_time() == "00:30"


def _session(tutor, student, start, duration):
    return Session(tutor_id=tutor.id, student_id=student.id, subject="Mathematics",
                   session_date=date(2026, 8, 10), start_time=start,
                   duration_minutes=duration)


def test_overlapping_sessions_are_detected(make_tutor, make_student):
    tutor, student = make_tutor(), make_student()
    a = _session(tutor, student, "15:00", 60)
    b = _session(tutor, student, "15:30", 60)
    assert a.overlaps(b) and b.overlaps(a)


def test_back_to_back_sessions_do_not_overlap(make_tutor, make_student):
    """15:00-16:00 and 16:00-17:00 are consecutive, not conflicting."""
    tutor, student = make_tutor(), make_student()
    a = _session(tutor, student, "15:00", 60)
    b = _session(tutor, student, "16:00", 60)
    assert not a.overlaps(b)


# --------------------------------------------------------------------------
# find_clash: the tutor and the room each only hold one session at a time
# --------------------------------------------------------------------------

def _book(tutor, student, start, duration=60, room="Room 1", status="booked"):
    session = Session(tutor_id=tutor.id, student_id=student.id, subject="Mathematics",
                      session_date=date(2026, 8, 10), start_time=start,
                      duration_minutes=duration, room=room, status=status)
    from app.models import db
    db.session.add(session)
    db.session.commit()
    return session


def test_find_clash_reports_a_tutor_conflict(make_tutor, make_student):
    tutor, student = make_tutor(), make_student()
    _book(tutor, student, "15:00", room="Room 1")
    clash, kind = Session.find_clash(tutor.id, date(2026, 8, 10), "15:30", 60, "Room 2")
    assert kind == "tutor" and clash is not None


def test_find_clash_reports_a_room_conflict(make_tutor, make_student):
    """A different tutor in the same room at the same time still clashes."""
    tutor, student = make_tutor(), make_student()
    other = make_tutor(name="Helen Vasquez", windows=[])
    _book(tutor, student, "15:00", room="Room 1")
    clash, kind = Session.find_clash(other.id, date(2026, 8, 10), "15:30", 60, "room 1")
    assert kind == "room" and clash is not None


def test_find_clash_ignores_cancelled_sessions(make_tutor, make_student):
    tutor, student = make_tutor(), make_student()
    _book(tutor, student, "15:00", room="Room 1", status="cancelled")
    assert Session.find_clash(tutor.id, date(2026, 8, 10), "15:30", 60, "Room 1") == (None, None)


def test_find_clash_returns_nothing_for_a_free_slot(make_tutor, make_student):
    tutor, student = make_tutor(), make_student()
    _book(tutor, student, "15:00", room="Room 1")
    assert Session.find_clash(tutor.id, date(2026, 8, 10), "17:00", 60, "Room 2") == (None, None)


def test_find_clash_ignores_other_weekdays(make_tutor, make_student):
    tutor, student = make_tutor(), make_student()
    _book(tutor, student, "15:00", room="Room 1")
    assert Session.find_clash(tutor.id, date(2026, 8, 11), "15:30", 60, "Room 1") == (None, None)


def test_find_clash_can_exclude_the_session_being_moved(make_tutor, make_student):
    """Rescheduling a session must not detect the session as its own clash."""
    tutor, student = make_tutor(), make_student()
    existing = _book(tutor, student, "15:00", room="Room 1")
    clash, kind = Session.find_clash(tutor.id, date(2026, 8, 10), "15:15", 60, "Room 1",
                                     exclude_id=existing.id)
    assert (clash, kind) == (None, None)


def test_find_clash_ignores_a_blank_room(make_tutor, make_student):
    """Sessions with no room recorded cannot conflict on room."""
    tutor, student = make_tutor(), make_student()
    other = make_tutor(name="Helen Vasquez", windows=[])
    _book(tutor, student, "15:00", room="")
    assert Session.find_clash(other.id, date(2026, 8, 10), "15:30", 60, "") == (None, None)
