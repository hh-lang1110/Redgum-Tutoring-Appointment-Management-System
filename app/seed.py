"""Seed data for local development.

Author: Vivian (Business & Requirements Lead)

Run with:
    flask --app run.py seed-db
"""
from .models import Booking, Student, Tutor, db


def seed_database():
    if Tutor.query.first() is not None:
        print("Database already contains data; skipping seed.")
        return

    t1 = Tutor(name="Sarah Mitchell", subjects="Math,Physics",
               qualification="M.Sc. Mathematics; 8 yrs tutoring",
               phone="0412-000-101", email="s.mitchell@redgum.edu.au",
               availability_note="Mon–Fri afternoons")
    t2 = Tutor(name="James O'Neill", subjects="Chemistry,Biology",
               qualification="B.Sc. Chemistry; 5 yrs tutoring",
               phone="0412-000-102", email="j.oneill@redgum.edu.au",
               availability_note="Tue–Sat")
    t3 = Tutor(name="Aisha Patel", subjects="English,History",
               qualification="M.A. Literature; 10 yrs tutoring",
               phone="0412-000-103", email="a.patel@redgum.edu.au",
               availability_note="Mon–Thu evenings")

    s1 = Student(name="Tom Wilson", grade_level="Year 10",
                 parent_name="Robert Wilson", parent_phone="0420-000-201",
                 parent_email="r.wilson@example.com",
                 enrolled_subjects="Math,Physics")
    s2 = Student(name="Emma Chen", grade_level="Year 11",
                 parent_name="Lina Chen", parent_phone="0420-000-202",
                 parent_email="l.chen@example.com",
                 enrolled_subjects="Chemistry,Biology")
    s3 = Student(name="Lucas Brown", grade_level="Year 9",
                 parent_name="Maria Brown", parent_phone="0420-000-203",
                 parent_email="m.brown@example.com",
                 enrolled_subjects="English,History")

    db.session.add_all([t1, t2, t3, s1, s2, s3])
    db.session.commit()

    bookings = [
        Booking(tutor_id=t1.id, student_id=s1.id, subject="Math",
                weekday=0, start_time="15:00", duration_minutes=60, room="Room 1"),
        Booking(tutor_id=t1.id, student_id=s1.id, subject="Physics",
                weekday=2, start_time="16:00", duration_minutes=90, room="Room 1"),
        Booking(tutor_id=t2.id, student_id=s2.id, subject="Chemistry",
                weekday=1, start_time="17:00", duration_minutes=60, room="Room 2"),
        Booking(tutor_id=t3.id, student_id=s3.id, subject="English",
                weekday=3, start_time="18:00", duration_minutes=60, room="Room 3"),
    ]
    db.session.add_all(bookings)
    db.session.commit()
    print("Seed data inserted: 3 tutors, 3 students, 4 bookings.")
