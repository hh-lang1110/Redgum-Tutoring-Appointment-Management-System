"""Seed data aligned with case-study Document A (Tomas availability) and
Document B (Week 5 diary). Dates: 11-15 August 2026 (Tue-Sat)."""
from datetime import date
from .models import db, Tutor, TutorAvailability, Student, Session


def seed_database():
    if Tutor.query.first() is not None:
        print("Database already contains data; skipping seed.")
        return

    # Tutors
    tomas = Tutor(name="Tomas Ferreira",
                  subjects="Physics, Chemistry, Mathematics, Maths Methods",
                  qualification="BSc (Hons) Physics, GradDipEd",
                  phone="0407 512 884",
                  email="tomas.ferreira@redgumtutoring.example")
    helen = Tutor(name="Helen Vasquez",
                  subjects="Mathematics, Maths Methods, Chemistry",
                  qualification="MTeach (Secondary Mathematics)",
                  phone="(07) 3812 6640",
                  email="helen.vasquez@redgumtutoring.example")

    db.session.add_all([tomas, helen])
    db.session.commit()

    # Tomas availability (Document A): Tue 15:30-19:00, Wed 15:30-18:00,
    # Thu 16:00-18:30, Fri none, Sat 09:00-12:30
    avails = [
        TutorAvailability(tutor_id=tomas.id, day_of_week=1, start_time="15:30", end_time="19:00"),
        TutorAvailability(tutor_id=tomas.id, day_of_week=2, start_time="15:30", end_time="18:00"),
        TutorAvailability(tutor_id=tomas.id, day_of_week=3, start_time="16:00", end_time="18:30"),
        TutorAvailability(tutor_id=tomas.id, day_of_week=5, start_time="09:00", end_time="12:30"),
        # Helen: Wed 15:30-19:00, Sat 10:15-12:00
        TutorAvailability(tutor_id=helen.id, day_of_week=2, start_time="15:30", end_time="19:00"),
        TutorAvailability(tutor_id=helen.id, day_of_week=5, start_time="10:00", end_time="13:00"),
    ]
    db.session.add_all(avails)

    # Students (Document B)
    students = [
        Student(name="Ella Nguyen", year_level="Year 11",
                parent_name="Mrs Nguyen", parent_phone="0411-000-001",
                parent_email="nguyen.family@example.com",
                enrolled_subjects="Physics"),
        Student(name="Jayden Pike", year_level="Year 10",
                parent_name="Mrs Pike", parent_phone="0411-000-002",
                parent_email="pike.family@example.com",
                enrolled_subjects="Mathematics"),
        Student(name="Sara Habib", year_level="Year 12",
                parent_name="Mr Habib", parent_phone="0411-000-003",
                parent_email="habib.family@example.com",
                enrolled_subjects="Chemistry"),
        Student(name="Oliver Brandt", year_level="Year 9",
                parent_name="Mrs Brandt", parent_phone="0411-000-004",
                parent_email="brandt.family@example.com",
                enrolled_subjects="Mathematics"),
        Student(name="Mia Okafor", year_level="Year 12",
                parent_name="Mrs Okafor", parent_phone="0411-000-005",
                parent_email="okafor.family@example.com",
                enrolled_subjects="Maths Methods"),
        Student(name="Kai Lombardo", year_level="Year 11",
                parent_name="Mr Lombardo", parent_phone="0411-000-006",
                parent_email="lombardo.family@example.com",
                enrolled_subjects="Physics"),
    ]
    db.session.add_all(students)
    db.session.commit()
    by_name = {s.name: s for s in students}

    # Sessions from Document B (Week 5: Tue 11 Aug - Sat 15 Aug 2026)
    sessions = [
        Session(tutor_id=tomas.id, student_id=by_name["Ella Nguyen"].id,
                subject="Physics", session_date=date(2026, 8, 11),
                start_time="15:30", duration_minutes=60, room="Room 1",
                status="attended"),
        Session(tutor_id=tomas.id, student_id=by_name["Jayden Pike"].id,
                subject="Mathematics", session_date=date(2026, 8, 11),
                start_time="16:45", duration_minutes=60, room="Room 1",
                status="missed"),
        Session(tutor_id=tomas.id, student_id=by_name["Sara Habib"].id,
                subject="Chemistry", session_date=date(2026, 8, 11),
                start_time="18:00", duration_minutes=60, room="Room 2",
                status="attended"),
        Session(tutor_id=helen.id, student_id=by_name["Oliver Brandt"].id,
                subject="Mathematics", session_date=date(2026, 8, 12),
                start_time="15:30", duration_minutes=60, room="Room 2",
                status="attended"),
        Session(tutor_id=helen.id, student_id=by_name["Mia Okafor"].id,
                subject="Maths Methods", session_date=date(2026, 8, 12),
                start_time="16:45", duration_minutes=90, room="Room 1",
                status="attended"),
        Session(tutor_id=tomas.id, student_id=by_name["Ella Nguyen"].id,
                subject="Physics", session_date=date(2026, 8, 13),
                start_time="16:00", duration_minutes=60, room="Room 1",
                status="attended"),
        Session(tutor_id=tomas.id, student_id=by_name["Kai Lombardo"].id,
                subject="Physics", session_date=date(2026, 8, 13),
                start_time="17:15", duration_minutes=60, room="Room 3",
                status="cancelled"),
        Session(tutor_id=tomas.id, student_id=by_name["Jayden Pike"].id,
                subject="Mathematics", session_date=date(2026, 8, 15),
                start_time="09:00", duration_minutes=60, room="Room 1",
                status="attended"),
        Session(tutor_id=helen.id, student_id=by_name["Sara Habib"].id,
                subject="Chemistry", session_date=date(2026, 8, 15),
                start_time="10:15", duration_minutes=90, room="Room 2",
                status="attended"),
        Session(tutor_id=helen.id, student_id=by_name["Oliver Brandt"].id,
                subject="Mathematics", session_date=date(2026, 8, 15),
                start_time="12:00", duration_minutes=60, room="Room 2",
                status="cancelled"),
    ]
    db.session.add_all(sessions)
    db.session.commit()
    print(f"Seed: {len(avails)} availability windows, "
          f"{len(students)} students, {len(sessions)} sessions.")
