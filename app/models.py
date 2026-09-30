"""SQLAlchemy models for Redgum Tutoring.

Domain model aligned with the case study:
- Tutor has availability windows (day_of_week, start, end).
- Session books one student with one tutor on a real date, with a status lifecycle.
- Core rule: a session must fall entirely inside one of the tutor's availability
  windows for that weekday.
- Each session records the room it occupies, so the centre can publish a
  room-by-room view alongside the tutor and student views.

Author: Vivian (Business & Requirements); implementation by Charon (Technical Lead).
"""
from datetime import UTC, datetime, time
from datetime import date as date_cls

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


WEEKDAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday",
                 "Friday", "Saturday", "Sunday"]

SESSION_STATUSES = ["booked", "attended", "cancelled", "missed"]


def _utcnow():
    """Current UTC time as a naive datetime, matching the DateTime columns.

    ``datetime.utcnow()`` is deprecated from Python 3.12 and returns a naive
    value that is easy to mistake for local time. Deriving from an aware
    ``now(timezone.utc)`` keeps the intent explicit while storing the same
    naive-UTC values the existing columns and rows already hold.
    """
    return datetime.now(UTC).replace(tzinfo=None)


def to_minutes(value):
    """Minutes past midnight for an 'HH:MM' string, or None if it is invalid."""
    if not value:
        return None
    try:
        hh, mm = str(value).split(":")
        hours, minutes = int(hh), int(mm)
    except (AttributeError, ValueError):
        return None
    if not (0 <= hours <= 23 and 0 <= minutes <= 59):
        return None
    return hours * 60 + minutes


def _parse_hhmm(value):
    """A datetime.time for an 'HH:MM' string, or None if it is invalid."""
    total = to_minutes(value)
    return None if total is None else time(total // 60, total % 60)


class Tutor(db.Model):
    __tablename__ = "tutors"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    subjects = db.Column(db.String(255), nullable=False)
    qualification = db.Column(db.String(120), default="")
    phone = db.Column(db.String(40), default="")
    email = db.Column(db.String(120), default="")
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=_utcnow)

    availability = db.relationship(
        "TutorAvailability", back_populates="tutor",
        cascade="all, delete-orphan", lazy="selectin",
    )
    sessions = db.relationship("Session", back_populates="tutor", lazy="dynamic")

    def subject_list(self):
        return [s.strip() for s in (self.subjects or "").split(",") if s.strip()]

    def teaches(self, subject):
        """True if ``subject`` is one this tutor is listed to teach."""
        wanted = (subject or "").strip().casefold()
        return bool(wanted) and wanted in {s.casefold() for s in self.subject_list()}

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
    parent_name = db.Column(db.String(120), default="")
    parent_phone = db.Column(db.String(40), default="")
    parent_email = db.Column(db.String(120), default="")
    enrolled_subjects = db.Column(db.String(255), default="")
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=_utcnow)

    sessions = db.relationship("Session", back_populates="student", lazy="dynamic")

    def subject_list(self):
        return [s.strip() for s in (self.enrolled_subjects or "").split(",") if s.strip()]

    def enrolled_in(self, subject):
        """True if the student is enrolled in ``subject``."""
        wanted = (subject or "").strip().casefold()
        return bool(wanted) and wanted in {s.casefold() for s in self.subject_list()}


class Session(db.Model):
    __tablename__ = "sessions"

    id = db.Column(db.Integer, primary_key=True)
    tutor_id = db.Column(db.Integer, db.ForeignKey("tutors.id"), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    subject = db.Column(db.String(80), nullable=False)
    session_date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.String(5), nullable=False)
    duration_minutes = db.Column(db.Integer, default=60, nullable=False)
    room = db.Column(db.String(40), default="")
    status = db.Column(db.String(20), default="booked", nullable=False)
    notes = db.Column(db.String(255), default="")
    created_at = db.Column(db.DateTime, default=_utcnow)

    tutor = db.relationship("Tutor", back_populates="sessions")
    student = db.relationship("Student", back_populates="sessions")

    def start_minutes(self):
        """Minutes past midnight for the session start, or None if invalid."""
        return to_minutes(self.start_time)

    def end_minutes(self):
        """Minutes past midnight for the session end, or None if invalid."""
        start = self.start_minutes()
        return None if start is None else start + int(self.duration_minutes or 60)

    def end_time(self):
        total = self.end_minutes()
        if total is None:
            return self.start_time
        return f"{(total // 60) % 24:02d}:{total % 60:02d}"

    def overlaps(self, other):
        """True if this session's time range intersects ``other``'s."""
        a_start, a_end = self.start_minutes(), self.end_minutes()
        b_start, b_end = other.start_minutes(), other.end_minutes()
        if None in (a_start, a_end, b_start, b_end):
            return False
        return a_start < b_end and b_start < a_end

    @staticmethod
    def find_clash(tutor_id, session_date, start_time, duration_minutes,
                   room="", exclude_id=None):
        """Find an existing session a proposed booking would clash with.

        A clash is either the same tutor or the same room already committed
        to an overlapping time on the same day. Cancelled sessions occupy
        neither, so they are skipped.

        ``exclude_id`` lets a session being rescheduled ignore itself.

        Returns ``(session, reason)`` with reason 'tutor' or 'room', or
        ``(None, None)`` when the slot is free.
        """
        probe = Session(tutor_id=tutor_id, session_date=session_date,
                        start_time=start_time, duration_minutes=duration_minutes)
        room_key = (room or "").strip().casefold()
        same_day = Session.query.filter(
            Session.session_date == session_date,
            Session.status != "cancelled",
        )
        if exclude_id is not None:
            same_day = same_day.filter(Session.id != exclude_id)
        for existing in same_day:
            if not existing.overlaps(probe):
                continue
            if existing.tutor_id == tutor_id:
                return existing, "tutor"
            if room_key and (existing.room or "").strip().casefold() == room_key:
                return existing, "room"
        return None, None

    def weekday(self):
        if isinstance(self.session_date, date_cls):
            return self.session_date.weekday()
        return None

    def weekday_name(self):
        w = self.weekday()
        return WEEKDAY_NAMES[w] if w is not None else "?"
