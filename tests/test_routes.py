"""Roster management, input validation and error handling."""
from app.models import Student, Tutor, TutorAvailability
from app.validation import MAX_LENGTH


def test_all_main_pages_render(client, seeded):
    for url in ["/", "/schedule/", "/sessions/", "/tutors/", "/students/", "/stats/"]:
        response = client.get(url, follow_redirects=True)
        assert response.status_code == 200, url


# --------------------------------------------------------------------------
# Tutors
# --------------------------------------------------------------------------

def test_tutor_can_be_created_and_edited(client, app):
    response = client.post("/tutors/new", data={
        "name": "Tomas Ferreira", "subjects": "Mathematics",
        "qualification": "BSc", "phone": "0400 000 000", "email": "t@example.com",
    }, follow_redirects=True)
    assert response.status_code == 200
    tutor = Tutor.query.one()
    assert tutor.qualification == "BSc"

    client.post(f"/tutors/{tutor.id}", data={
        "name": "Tomas Ferreira", "subjects": "Mathematics, Physics",
        "qualification": "MSc", "phone": "0400 000 000", "email": "t@example.com",
    }, follow_redirects=True)
    assert Tutor.query.one().qualification == "MSc"


def test_tutor_without_a_name_is_refused(client, app):
    client.post("/tutors/new", data={"name": "", "subjects": "Mathematics"},
                follow_redirects=True)
    assert Tutor.query.count() == 0


def test_over_long_tutor_name_is_refused_not_truncated(client, app):
    """SQLite stores over-long strings silently; the route must refuse first."""
    too_long = "x" * (MAX_LENGTH["name"] + 1)
    response = client.post("/tutors/new",
                           data={"name": too_long, "subjects": "Mathematics"},
                           follow_redirects=True)
    assert b"characters or fewer" in response.data
    assert Tutor.query.count() == 0


def test_editing_a_tutor_does_not_wipe_absent_fields(client, app, make_tutor):
    tutor = make_tutor()
    tutor.email = "keep@example.com"
    from app.models import db
    db.session.commit()
    client.post(f"/tutors/{tutor.id}", data={"name": "Tomas Ferreira",
                                             "subjects": "Mathematics"},
                follow_redirects=True)
    assert Tutor.query.one().email == "keep@example.com"


def test_deactivate_keeps_the_tutor_record(client, app, make_tutor):
    tutor = make_tutor()
    client.post(f"/tutors/{tutor.id}",
                data={"name": tutor.name, "subjects": tutor.subjects, "deactivate": "1"},
                follow_redirects=True)
    assert Tutor.query.one().is_active is False


# --------------------------------------------------------------------------
# Availability windows
# --------------------------------------------------------------------------

def add_window(client, tutor, weekday=0, start="15:00", end="19:00"):
    return client.post(f"/tutors/{tutor.id}/availability/add",
                       data={"day_of_week": weekday, "start_time": start, "end_time": end},
                       follow_redirects=True)


def test_valid_window_is_stored(client, app, make_tutor):
    tutor = make_tutor(windows=[])
    assert add_window(client, tutor).status_code == 200
    assert TutorAvailability.query.count() == 1


def test_reversed_window_is_refused(client, app, make_tutor):
    tutor = make_tutor(windows=[])
    response = add_window(client, tutor, start="19:00", end="15:00")
    assert b"must end after it starts" in response.data
    assert TutorAvailability.query.count() == 0


def test_malformed_time_is_refused(client, app, make_tutor):
    tutor = make_tutor(windows=[])
    response = add_window(client, tutor, start="25:00")
    assert b"24-hour HH:MM" in response.data
    assert TutorAvailability.query.count() == 0


def test_overlapping_window_is_refused(client, app, make_tutor):
    tutor = make_tutor(windows=[(0, "15:00", "19:00")])
    response = add_window(client, tutor, start="18:00", end="20:00")
    assert b"overlaps the existing window" in response.data
    assert TutorAvailability.query.count() == 1


def test_adjacent_window_is_allowed(client, app, make_tutor):
    """15:00-19:00 plus 19:00-21:00 is a split shift, not an overlap."""
    tutor = make_tutor(windows=[(0, "15:00", "19:00")])
    assert add_window(client, tutor, start="19:00", end="21:00").status_code == 200
    assert TutorAvailability.query.count() == 2


def test_window_on_a_different_day_does_not_overlap(client, app, make_tutor):
    tutor = make_tutor(windows=[(0, "15:00", "19:00")])
    assert add_window(client, tutor, weekday=1, start="15:00",
                      end="19:00").status_code == 200
    assert TutorAvailability.query.count() == 2


def test_invalid_weekday_is_refused(client, app, make_tutor):
    tutor = make_tutor(windows=[])
    response = add_window(client, tutor, weekday=9)
    assert b"Choose a weekday" in response.data
    assert TutorAvailability.query.count() == 0


def test_sunday_availability_is_refused(client, app, make_tutor):
    """Sunday windows could never be used, since the grid stops at Saturday."""
    tutor = make_tutor(windows=[])
    response = add_window(client, tutor, weekday=6)
    assert b"Choose a weekday" in response.data
    assert TutorAvailability.query.count() == 0


def test_the_day_dropdown_offers_monday_to_saturday(client, app, make_tutor):
    tutor = make_tutor(windows=[])
    body = client.get(f"/tutors/{tutor.id}").data.decode()
    dropdown = body.split('name="day_of_week"')[1].split("</select>")[0]
    assert "Monday" in dropdown and "Saturday" in dropdown
    assert "Sunday" not in dropdown


def test_window_can_be_deleted(client, app, make_tutor):
    make_tutor(windows=[(0, "15:00", "19:00")])
    window = TutorAvailability.query.one()
    client.post(f"/tutors/availability/{window.id}/delete", follow_redirects=True)
    assert TutorAvailability.query.count() == 0


# --------------------------------------------------------------------------
# Students
# --------------------------------------------------------------------------

def test_student_can_be_created(client, app):
    client.post("/students/new", data={
        "name": "Ella Nguyen", "year_level": "Year 10",
        "enrolled_subjects": "Mathematics", "parent_name": "Mia Nguyen",
        "parent_phone": "0400 111 222", "parent_email": "mia@example.com",
    }, follow_redirects=True)
    student = Student.query.one()
    assert student.parent_name == "Mia Nguyen"


def test_student_without_a_name_is_refused(client, app):
    client.post("/students/new", data={"name": "   "}, follow_redirects=True)
    assert Student.query.count() == 0


def test_over_long_student_email_is_refused(client, app):
    response = client.post("/students/new", data={
        "name": "Ella Nguyen", "parent_email": "x" * (MAX_LENGTH["parent_email"] + 1),
    }, follow_redirects=True)
    assert b"characters or fewer" in response.data
    assert Student.query.count() == 0


def test_student_session_history_renders(client, seeded):
    student = Student.query.first()
    response = client.get(f"/students/{student.id}/sessions")
    assert response.status_code == 200


# --------------------------------------------------------------------------
# Session status
# --------------------------------------------------------------------------

def test_status_can_be_changed(client, app, make_tutor, make_student):
    from datetime import date

    from app.models import Session, db
    session = Session(tutor_id=make_tutor().id, student_id=make_student().id,
                      subject="Mathematics", session_date=date(2026, 8, 10),
                      start_time="16:00", duration_minutes=60, room="Room 1")
    db.session.add(session)
    db.session.commit()
    client.post(f"/sessions/{session.id}/status", data={"status": "attended"},
                follow_redirects=True)
    assert Session.query.one().status == "attended"


def test_unknown_status_is_rejected(client, app, make_tutor, make_student):
    from datetime import date

    from app.models import Session, db
    session = Session(tutor_id=make_tutor().id, student_id=make_student().id,
                      subject="Mathematics", session_date=date(2026, 8, 10),
                      start_time="16:00", duration_minutes=60, room="Room 1")
    db.session.add(session)
    db.session.commit()
    response = client.post(f"/sessions/{session.id}/status", data={"status": "banana"})
    assert response.status_code == 400


def test_external_referrer_is_not_followed(client, app, make_tutor, make_student):
    """An attacker-set Referer must not turn the endpoint into an open redirect."""
    from datetime import date

    from app.models import Session, db
    session = Session(tutor_id=make_tutor().id, student_id=make_student().id,
                      subject="Mathematics", session_date=date(2026, 8, 10),
                      start_time="16:00", duration_minutes=60, room="Room 1")
    db.session.add(session)
    db.session.commit()
    response = client.post(f"/sessions/{session.id}/status", data={"status": "attended"},
                           headers={"Referer": "https://evil.example.com/phish"})
    assert response.status_code == 302
    assert "evil.example.com" not in response.headers["Location"]
    assert response.headers["Location"].endswith("/sessions/")


# --------------------------------------------------------------------------
# Errors
# --------------------------------------------------------------------------

def test_missing_record_renders_the_404_page(client, app):
    response = client.get("/tutors/9999")
    assert response.status_code == 404
    assert b"Page not found" in response.data


def test_unexpected_error_renders_the_500_page(client, app):
    @app.route("/boom")
    def boom():
        raise RuntimeError("boom")

    # In testing Flask re-raises instead of returning a response; turn that
    # off so the registered handler is what we are actually exercising.
    app.config["PROPAGATE_EXCEPTIONS"] = False
    response = client.get("/boom")
    assert response.status_code == 500
    assert b"Something went wrong" in response.data
