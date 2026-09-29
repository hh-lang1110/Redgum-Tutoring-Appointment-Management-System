"""SQLAlchemy models for Redgum Tutoring.

Domain model aligned with the case study:
- Tutor has availability windows (day_of_week, start, end).
- Session books one student with one tutor on a real date, with a status lifecycle.
- Core rule: a session must fall entirely inside one of the tutor's availability
  windows for that weekday. Room allocation and double-booking detection are
  explicitly out of scope per the brief.

Author: Vivian (Business & Requirements); implementation by Charon (Technical Lead).
"""
from datetime import datetime, time, date as date_cls

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


WEEKDAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday",
                 "Friday", "Saturday", "Sunday"]

SESSION_STATUSES = ["booked", "attended", "cancelled", "missed"]


def _parse_hhmm(value):
    if not value:
        return None
    try:
        hh, mm = value.split(":")
        return time(int(hh), int(mm))
    except Exception:
        return None


class Tutor(db.Model):
    __tablename__ = "tutors"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    subjects = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(40), default="")
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    availability = db.relationship(
        "TutorAvailability", back_populates="tutor",
        cascade="all, delete-orphan", lazy="selectin",
    )
    sessions = db.relationship("Session", back_populates="tutor", lazy="dynamic")

    def subject_list(self):
        return [s.strip() for s in (self.subjects or "").split(",") if s.strip()]

    def windows_for(self, weekday):
        return [w for w in self.availability if w.day_of_week == weekday]

    def can_fit(self, weekday, start_time_str, duration_min):
        start = _parse_hhmm(start_time_str)
        if start is None:
            return False, "Invalid start time."
        end_min = start.hour * 60 + start.minute + int(duration_min or 60)
        windows = self.windows_for(weekday)
        if not windows:
            return False, (
                f"{self.name} has no availability recorded for "
                f"{WEEKDAY_NAMES[weekday]}."
            )
        for w in windows:
            ws = _parse_hhmm(w.start_time)
            we = _parse_hhmm(w.end_time)
            if ws is None or we is None:
                continue
            ws_min = ws.hour * 60 + ws.minute
            we_min = we.hour * 60 + we.minute
            if ws_min <= start.hour * 60 + start.minute and end_min <= we_min:
                return True, ""
        shown = ", ".join(f"{w.start_time}-{w.end_time}" for w in windows)
        return False, (
            f"{self.name} is only available {WEEKDAY_NAMES[weekday]} {shown}; "
            f"the requested session does not fit inside any window."
        )


class TutorAvailability(db.Model):
    __tablename__ = "tutor_availability"

    id = db.Column(db.Integer, primary_key=True)
    tutor_id = db.Column(db.Integer, db.ForeignKey("tutors.id"), nullable=False)
    day_of_week = db.Column(db.Integer, nullable=False)
    start_time = db.Column(db.String(5), nullable=False)
    end_time = db.Column(db.String(5), nullable=False)

    tutor = db.relationship("Tutor", back_populates="availability")

    def day_name(self):
        if 0 <= self.day_of_week < 7:
            return WEEKDAY_NAMES[self.day_of_week]
        return "?"


class Student(db.Model):
    __tablename__ = "students"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    year_level = db.Column(db.String(20), default="")
    parent_contact = db.Column(db.String(120), default="")
    parent_phone = db.Column(db.String(40), default="")
    enrolled_subjects = db.Column(db.String(255), default="")
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    sessions = db.relationship("Session", back_populates="student", lazy="dynamic")

    def subject_list(self):
        return [s.strip() for s in (self.enrolled_subjects or "").split(",") if s.strip()]


class Session(db.Model):
    __tablename__ = "sessions"

    id = db.Column(db.Integer, primary_key=True)
    tutor_id = db.Column(db.Integer, db.ForeignKey("tutors.id"), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    subject = db.Column(db.String(80), nullable=False)
    session_date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.String(5), nullable=False)
    duration_minutes = db.Column(db.Integer, default=60, nullable=False)
    status = db.Column(db.String(20), default="booked", nullable=False)
    notes = db.Column(db.String(255), default="")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    tutor = db.relationship("Tutor", back_populates="sessions")
    student = db.relationship("Student", back_populates="sessions")

    def end_time(self):
        s = _parse_hhmm(self.start_time)
        if s is None:
            return self.start_time
        total = s.hour * 60 + s.minute + int(self.duration_minutes or 60)
        return f"{(total // 60) % 24:02d}:{total % 60:02d}"

    def weekday(self):
        if isinstance(self.session_date, date_cls):
            return self.session_date.weekday()
        return None

    def weekday_name(self):
        w = self.weekday()
        return WEEKDAY_NAMES[w] if w is not None else "?"
