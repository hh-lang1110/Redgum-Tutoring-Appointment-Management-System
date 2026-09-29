"""Statistics dashboard.

Author: Charon (Technical Lead)
"""
from collections import Counter

from flask import Blueprint, render_template

from ..models import Booking, Student, Tutor

bp = Blueprint("stats", __name__)


@bp.route("/")
def dashboard():
    active_tutors = Tutor.query.filter_by(is_active=True).count()
    active_students = Student.query.filter_by(is_active=True).count()
    weekly_bookings = Booking.query.filter_by(is_cancelled=False).count()

    subject_counter = Counter(
        b.subject for b in Booking.query.filter_by(is_cancelled=False).all()
    )
    subject_distribution = subject_counter.most_common()

    return render_template(
        "stats/dashboard.html",
        active_tutors=active_tutors,
        active_students=active_students,
        weekly_bookings=weekly_bookings,
        subject_distribution=subject_distribution,
    )
