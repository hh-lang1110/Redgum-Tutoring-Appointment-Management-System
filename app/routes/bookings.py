"""Lesson booking routes, with tutor/room conflict detection.

Author: Charon (Technical Lead)
"""
from datetime import datetime

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

from ..models import Booking, Student, Tutor, db

bp = Blueprint("bookings", __name__)


def _to_minutes(hhmm: str) -> int:
    h, m = hhmm.split(":")
    return int(h) * 60 + int(m)


def _find_conflict(tutor_id, room, weekday, start_time, duration, exclude_id=None):
    """Return an overlapping booking for the same tutor OR same room, or None."""
    start = _to_minutes(start_time)
    end = start + int(duration)

    candidates = Booking.query.filter(
        Booking.is_cancelled.is_(False),
        Booking.weekday == weekday,
    ).all()

    for b in candidates:
        if exclude_id and b.id == exclude_id:
            continue
        b_start = _to_minutes(b.start_time)
        b_end = b_start + int(b.duration_minutes)
        overlap = start < b_end and b_start < end
        if not overlap:
            continue
        if b.tutor_id == tutor_id:
            return ("tutor", b)
        if room and b.room == room:
            return ("room", b)
    return None


@bp.route("/")
def list_bookings():
    bookings = (
        Booking.query.filter_by(is_cancelled=False)
        .order_by(Booking.weekday, Booking.start_time)
        .all()
    )
    return render_template("bookings/list.html", bookings=bookings)


@bp.route("/new", methods=["GET", "POST"])
def create_booking():
    tutors = Tutor.query.filter_by(is_active=True).order_by(Tutor.name).all()
    students = Student.query.filter_by(is_active=True).order_by(Student.name).all()

    if request.method == "POST":
        tutor_id = int(request.form["tutor_id"])
        student_id = int(request.form["student_id"])
        subject = request.form["subject"].strip()
        weekday = int(request.form["weekday"])
        start_time = request.form["start_time"]
        duration = int(request.form.get("duration_minutes", 60))
        room = request.form.get("room", "").strip()

        tutor = Tutor.query.get_or_404(tutor_id)
        student = Student.query.get_or_404(student_id)

        # BR-4: subject must be taught by tutor and enrolled by student
        if subject not in tutor.subject_list():
            flash(f"{tutor.name} does not teach {subject}.", "danger")
            return render_template(
                "bookings/form.html", tutors=tutors, students=students, form=request.form
            )
        if subject not in student.subject_list():
            flash(f"{student.name} is not enrolled in {subject}.", "danger")
            return render_template(
                "bookings/form.html", tutors=tutors, students=students, form=request.form
            )

        conflict = _find_conflict(tutor_id, room, weekday, start_time, duration)
        if conflict:
            kind, existing = conflict
            flash(
                f"Conflict: {kind} is already booked for "
                f"{existing.weekday_name()} {existing.start_time} "
                f"({existing.tutor.name} / {existing.student.name}).",
                "danger",
            )
            return render_template(
                "bookings/form.html", tutors=tutors, students=students, form=request.form
            )

        b = Booking(
            tutor_id=tutor_id, student_id=student_id, subject=subject,
            weekday=weekday, start_time=start_time, duration_minutes=duration, room=room,
        )
        db.session.add(b)
        db.session.commit()
        flash("Booking created.", "success")
        return redirect(url_for("bookings.list_bookings"))

    return render_template("bookings/form.html", tutors=tutors, students=students, form=None)


@bp.route("/<int:booking_id>/cancel", methods=["POST"])
def cancel_booking(booking_id):
    b = Booking.query.get_or_404(booking_id)
    b.is_cancelled = True
    db.session.commit()
    flash("Booking cancelled.", "info")
    return redirect(url_for("bookings.list_bookings"))
