"""The booking rules, exercised through the HTTP endpoints.

The model tests cover the helpers in isolation; these check that the routes
actually apply them, because the rules are only worth anything if a booking
that breaks them is refused.
"""
from datetime import date

import pytest

from app.models import Session

MONDAY = "2026-08-10"      # weekday 0
TUESDAY = "2026-08-11"     # weekday 1


@pytest.fixture
def booking(make_tutor, make_student):
    """A tutor free 15:00-19:00 on Mondays and an enrolled student."""
    tutor = make_tutor(windows=[(0, "15:00", "19:00")])
    student = make_student()
    return tutor, student


def post_booking(client, tutor, student, **overrides):
    data = {
        "tutor_id": tutor.id,
        "student_id": student.id,
        "subject": "Mathematics",
        "session_date": MONDAY,
        "start_time": "16:00",
        "duration_minutes": "60",
        "room": "Room 1",
    }
    data.update(overrides)
    return client.post("/sessions/new", data=data, follow_redirects=True)


def test_valid_booking_is_created(client, app, booking):
    tutor, student = booking
    response = post_booking(client, tutor, student)
    assert b"Session booked" in response.data
    assert Session.query.count() == 1


def test_booking_inside_availability_is_accepted_at_the_edges(client, app, booking):
    tutor, student = booking
    assert b"Session booked" in post_booking(client, tutor, student,
                                             start_time="15:00",
                                             duration_minutes="240").data
    assert Session.query.count() == 1


def test_subject_the_tutor_does_not_teach_is_refused(client, app, booking):
    tutor, student = booking
    response = post_booking(client, tutor, student, subject="Chemistry")
    assert b"is not listed to teach" in response.data
    assert Session.query.count() == 0


def test_subject_the_student_is_not_enrolled_in_is_refused(client, app, make_tutor, make_student):
    tutor = make_tutor(subjects="Mathematics", windows=[(0, "15:00", "19:00")])
    student = make_student(subjects="Physics")
    response = post_booking(client, tutor, student, subject="Mathematics")
    assert b"is not enrolled in" in response.data
    assert Session.query.count() == 0


def test_booking_outside_availability_is_refused(client, app, booking):
    tutor, student = booking
    response = post_booking(client, tutor, student, start_time="09:00")
    assert b"only available" in response.data
    assert Session.query.count() == 0


def test_booking_on_a_day_with_no_availability_is_refused(client, app, booking):
    tutor, student = booking
    response = post_booking(client, tutor, student, session_date=TUESDAY)
    assert b"no availability" in response.data
    assert Session.query.count() == 0


def test_tutor_cannot_be_double_booked(client, app, booking):
    tutor, student = booking
    post_booking(client, tutor, student, start_time="16:00", room="Room 1")
    response = post_booking(client, tutor, student, start_time="16:30", room="Room 2")
    assert b"already booked" in response.data
    assert Session.query.count() == 1


def test_room_cannot_be_double_booked(client, app, booking, make_tutor, make_student):
    tutor, student = booking
    other_tutor = make_tutor(name="Helen Vasquez", windows=[(0, "15:00", "19:00")])
    other_student = make_student(name="Jayden Pike")
    post_booking(client, tutor, student, start_time="16:00", room="Room 1")
    response = post_booking(client, other_tutor, other_student,
                            start_time="16:30", room="Room 1")
    assert b"already booked" in response.data
    assert Session.query.count() == 1


def test_back_to_back_bookings_are_allowed(client, app, booking):
    """A 16:00-17:00 lesson and a 17:00-18:00 lesson do not conflict."""
    tutor, student = booking
    post_booking(client, tutor, student, start_time="16:00", duration_minutes="60")
    response = post_booking(client, tutor, student, start_time="17:00", duration_minutes="60")
    assert b"Session booked" in response.data
    assert Session.query.count() == 2


def test_cancelled_sessions_do_not_block_a_slot(client, app, booking):
    tutor, student = booking
    post_booking(client, tutor, student, start_time="16:00")
    session = Session.query.one()
    session.status = "cancelled"
    from app.models import db
    db.session.commit()
    assert b"Session booked" in post_booking(client, tutor, student, start_time="16:00").data


def test_missing_fields_are_refused(client, app, booking):
    tutor, student = booking
    response = client.post("/sessions/new",
                           data={"tutor_id": tutor.id, "student_id": student.id},
                           follow_redirects=True)
    assert b"All fields are required" in response.data
    assert Session.query.count() == 0


def test_unknown_tutor_id_returns_404(client, app, booking):
    tutor, student = booking
    response = client.post("/sessions/new", data={
        "tutor_id": 9999, "student_id": student.id, "subject": "Mathematics",
        "session_date": MONDAY, "start_time": "16:00", "duration_minutes": "60",
    })
    assert response.status_code == 404


# --------------------------------------------------------------------------
# Moving an existing session
# --------------------------------------------------------------------------

def test_move_to_a_free_slot_succeeds(client, app, booking):
    tutor, student = booking
    post_booking(client, tutor, student, start_time="16:00")
    session = Session.query.one()
    response = client.post(f"/sessions/{session.id}/move",
                           data={"session_date": MONDAY, "start_time": "18:00",
                                 "duration_minutes": "60", "room": "Room 1"},
                           follow_redirects=True)
    assert b"Session moved" in response.data
    assert Session.query.one().start_time == "18:00"


def test_moving_a_session_does_not_clash_with_itself(client, app, booking):
    """The session being moved must be excluded from its own clash check."""
    tutor, student = booking
    post_booking(client, tutor, student, start_time="16:00")
    session = Session.query.one()
    response = client.post(f"/sessions/{session.id}/move",
                           data={"session_date": MONDAY, "start_time": "16:00",
                                 "duration_minutes": "90", "room": "Room 1"},
                           follow_redirects=True)
    assert b"Session moved" in response.data
    assert Session.query.one().duration_minutes == 90


def test_move_onto_another_session_is_refused(client, app, booking):
    tutor, student = booking
    post_booking(client, tutor, student, start_time="16:00")
    other = make_second_session(tutor, student, "17:00")
    response = client.post(f"/sessions/{other.id}/move",
                           data={"session_date": MONDAY, "start_time": "16:30",
                                 "duration_minutes": "60", "room": "Room 2"},
                           follow_redirects=True)
    assert b"already booked" in response.data


def test_move_outside_availability_is_refused(client, app, booking):
    tutor, student = booking
    post_booking(client, tutor, student, start_time="16:00")
    session = Session.query.one()
    response = client.post(f"/sessions/{session.id}/move",
                           data={"session_date": MONDAY, "start_time": "08:00",
                                 "duration_minutes": "60", "room": "Room 1"},
                           follow_redirects=True)
    assert b"only available" in response.data
    assert Session.query.one().start_time == "16:00"


def test_zero_duration_is_refused(client, app, booking):
    tutor, student = booking
    response = post_booking(client, tutor, student, duration_minutes="0")
    assert b"at least" in response.data
    assert Session.query.count() == 0


def test_negative_duration_is_refused(client, app, booking):
    """A negative length must not be stored as a valid session."""
    tutor, student = booking
    response = post_booking(client, tutor, student, duration_minutes="-60")
    assert b"at least" in response.data
    assert Session.query.count() == 0


def test_absurd_duration_is_refused(client, app, booking):
    tutor, student = booking
    response = post_booking(client, tutor, student, duration_minutes="100000")
    assert b"no more than" in response.data
    assert Session.query.count() == 0


def test_negative_duration_is_refused_when_moving(client, app, booking):
    tutor, student = booking
    post_booking(client, tutor, student, start_time="16:00")
    session = Session.query.one()
    response = client.post(f"/sessions/{session.id}/move",
                           data={"session_date": MONDAY, "start_time": "16:00",
                                 "duration_minutes": "-120", "room": "Room 1"},
                           follow_redirects=True)
    assert b"at least" in response.data
    assert Session.query.one().duration_minutes == 60


def test_negative_duration_would_otherwise_evade_the_clash_check(client, app, booking):
    """Why the duration bound matters rather than being cosmetic.

    A session that ends before it starts fails every overlap comparison, so
    without the bound it could be booked straight on top of an existing
    lesson without the conflict check firing.
    """
    tutor, student = booking
    post_booking(client, tutor, student, start_time="16:00", duration_minutes="60")
    response = post_booking(client, tutor, student, start_time="16:30", duration_minutes="-60")
    assert b"at least" in response.data
    assert Session.query.count() == 1


# --------------------------------------------------------------------------
# The timetable covers Monday to Saturday (TT-1)
# --------------------------------------------------------------------------

SUNDAY = "2026-08-16"   # weekday 6


def test_sunday_booking_is_refused(client, app, make_tutor, make_student):
    """A Sunday session would be stored and counted but never displayed."""
    tutor = make_tutor(windows=[(6, "09:00", "12:00")])
    student = make_student()
    response = post_booking(client, tutor, student, session_date=SUNDAY,
                            start_time="09:30")
    assert b"Monday to Saturday" in response.data
    assert Session.query.count() == 0


def test_saturday_booking_is_still_allowed(client, app, make_tutor, make_student):
    tutor = make_tutor(windows=[(5, "09:00", "12:00")])
    student = make_student()
    response = post_booking(client, tutor, student, session_date="2026-08-15",
                            start_time="09:30")
    assert b"Session booked" in response.data


def test_moving_a_session_to_sunday_is_refused(client, app, booking):
    tutor, student = booking
    post_booking(client, tutor, student, start_time="16:00")
    session = Session.query.one()
    response = client.post(f"/sessions/{session.id}/move",
                           data={"session_date": SUNDAY, "start_time": "16:00",
                                 "duration_minutes": "60", "room": "Room 1"},
                           follow_redirects=True)
    assert b"Monday to Saturday" in response.data
    assert Session.query.one().session_date == date(2026, 8, 10)


def make_second_session(tutor, student, start_time):
    from app.models import db
    session = Session(tutor_id=tutor.id, student_id=student.id, subject="Mathematics",
                      session_date=date(2026, 8, 10), start_time=start_time,
                      duration_minutes=60, room="Room 1", status="booked")
    db.session.add(session)
    db.session.commit()
    return session
