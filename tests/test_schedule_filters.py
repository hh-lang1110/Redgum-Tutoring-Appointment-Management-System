"""Timetable filters (TT-2)."""
from datetime import date

import pytest

from app.models import Session, db

MONDAY = date(2026, 8, 10)
WEEK = "?week=2026-08-11"


@pytest.fixture
def timetable(app, make_tutor, make_student):
    """Two tutors, two students, three sessions in one week."""
    tomas = make_tutor(name="Tomas Ferreira", subjects="Mathematics",
                       windows=[(0, "15:00", "19:00")])
    helen = make_tutor(name="Helen Vasquez", subjects="Physics",
                       windows=[(0, "15:00", "19:00")])
    ella = make_student(name="Ella Nguyen", subjects="Mathematics")
    jayden = make_student(name="Jayden Pike", subjects="Physics")

    def add(tutor, student, subject, start, room):
        session = Session(tutor_id=tutor.id, student_id=student.id, subject=subject,
                          session_date=MONDAY, start_time=start, duration_minutes=60,
                          room=room, status="booked")
        db.session.add(session)
        db.session.commit()
        return session

    add(tomas, ella, "Mathematics", "15:00", "Room 1")
    add(tomas, jayden, "Physics", "16:00", "Room 2")
    add(helen, jayden, "Physics", "17:00", "Room 1")
    return {"tomas": tomas, "helen": helen, "ella": ella, "jayden": jayden}


def rows(response):
    """Count the session rows in the rendered grid."""
    return response.data.decode().count('<tr class=')


def test_unfiltered_grid_shows_every_session(client, timetable):
    assert rows(client.get("/schedule/" + WEEK)) == 3


def test_filtering_by_tutor_shows_only_that_tutors_sessions(client, timetable):
    response = client.get(f"/schedule/{WEEK}&tutor={timetable['tomas'].id}")
    assert rows(response) == 2
    assert b"Helen Vasquez" not in response.data.split(b"</select>")[1]


def test_tutor_filters_partition_the_week(client, timetable):
    """The two tutors' sessions must add up to the unfiltered total."""
    tomas = rows(client.get(f"/schedule/{WEEK}&tutor={timetable['tomas'].id}"))
    helen = rows(client.get(f"/schedule/{WEEK}&tutor={timetable['helen'].id}"))
    assert tomas + helen == 3


def test_filtering_by_student(client, timetable):
    response = client.get(f"/schedule/{WEEK}&student={timetable['ella'].id}")
    assert rows(response) == 1


def test_filtering_by_room(client, timetable):
    assert rows(client.get(f"/schedule/{WEEK}&room=Room%201")) == 2


def test_room_filter_ignores_case(client, timetable):
    upper = rows(client.get(f"/schedule/{WEEK}&room=Room%201"))
    lower = rows(client.get(f"/schedule/{WEEK}&room=room%201"))
    assert upper == lower == 2


def test_filters_combine(client, timetable):
    response = client.get(f"/schedule/{WEEK}&tutor={timetable['tomas'].id}&room=Room%201")
    assert rows(response) == 1


def test_filters_are_carried_into_week_navigation(client, timetable):
    """Stepping to the next week should keep the current view."""
    response = client.get(f"/schedule/{WEEK}&tutor={timetable['tomas'].id}")
    assert f"tutor={timetable['tomas'].id}".encode() in response.data
    assert b"week=2026-08-17" in response.data


def test_a_filter_matching_nothing_reports_zero(client, timetable):
    response = client.get(f"/schedule/{WEEK}&room=Room%2099")
    assert response.status_code == 200
    assert rows(response) == 0
    assert b"0 sessions match" in response.data


def test_unfiltered_view_has_no_match_summary(client, timetable):
    assert b"match the current filters" not in client.get("/schedule/" + WEEK).data


@pytest.mark.parametrize("query", [
    "&tutor=abc",       # not a number
    "&tutor=999999",    # no such tutor
    "&student=-1",
    "&room=%00",
])
def test_malformed_filters_do_not_error(client, timetable, query):
    assert client.get("/schedule/" + WEEK + query).status_code == 200


def test_cancelled_sessions_are_not_shown(client, timetable):
    session = Session.query.first()
    session.status = "cancelled"
    db.session.commit()
    assert rows(client.get("/schedule/" + WEEK)) == 2
