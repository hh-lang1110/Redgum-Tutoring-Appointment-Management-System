"""SQLAlchemy models for Redgum Tutoring Appointment Management System.

Author: Vivian (Business & Requirements Lead)
"""
from datetime import datetime

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Tutor(db.Model):
    """A tutor profile."""

    __tablename__ = "tutors"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    subjects = db.Column(db.String(255), nullable=False)  # CSV, e.g. "Math,Physics"
    qualification = db.Column(db.String(255), default="")
    phone = db.Column(db.String(40), default="")
    email = db.Column(db.String(120), default="")
    availability_note = db.Column(db.String(255), default="")
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    bookings = db.relationship("Booking", back_populates="tutor", lazy="dynamic")

    def subject_list(self):
        return [s.strip() for s in (self.subjects or "").split(",") if s.strip()]


class Student(db.Model):
    """A student profile."""

    __tablename__ = "students"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    grade_level = db.Column(db.String(40), default="")
    parent_name = db.Column(db.String(120), default="")
    parent_phone = db.Column(db.String(40), default="")
    parent_email = db.Column(db.String(120), default="")
    enrolled_subjects = db.Column(db.String(255), default="")  # CSV
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    bookings = db.relationship("Booking", back_populates="student", lazy="dynamic")

    def subject_list(self):
        return [s.strip() for s in (self.enrolled_subjects or "").split(",") if s.strip()]


class Booking(db.Model):
    """A booked lesson between a tutor and a student."""

    __tablename__ = "bookings"

    id = db.Column(db.Integer, primary_key=True)
    tutor_id = db.Column(db.Integer, db.ForeignKey("tutors.id"), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    subject = db.Column(db.String(80), nullable=False)
    weekday = db.Column(db.Integer, nullable=False)  # 0=Monday ... 5=Saturday
    start_time = db.Column(db.String(5), nullable=False)  # HH:MM
    duration_minutes = db.Column(db.Integer, default=60)
    room = db.Column(db.String(40), default="")
    is_cancelled = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    tutor = db.relationship("Tutor", back_populates="bookings")
    student = db.relationship("Student", back_populates="bookings")

    WEEKDAY_NAMES = [
        "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday",
    ]

    def weekday_name(self):
        if 0 <= self.weekday < len(self.WEEKDAY_NAMES):
            return self.WEEKDAY_NAMES[self.weekday]
        return "?"

    def end_time(self):
        """Return end time as HH:MM computed from start_time + duration."""
        try:
            hh, mm = [int(x) for x in self.start_time.split(":")]
        except Exception:
            return self.start_time
        total = hh * 60 + mm + int(self.duration_minutes or 60)
        return f"{(total // 60) % 24:02d}:{total % 60:02d}"
