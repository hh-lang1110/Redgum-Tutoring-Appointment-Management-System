"""Statistics dashboard.

Author: Liu (Project Manager).

The project charter lists a basic statistics dashboard as in scope
(ST-1 to ST-4), but the prototype never shipped one. This module supplies
the four operational numbers centre staff asked for: how many tutors and
students are active, how many lessons are booked this week, and how the
bookings split across subjects.
"""
from datetime import date, timedelta

from flask import Blueprint, render_template, request

from ..models import Session, Student, Tutor

bp = Blueprint("stats", __name__, url_prefix="/stats")


def week_bounds(anchor):
    """Return the Monday and Sunday bounding the week containing ``anchor``."""
    monday = anchor - timedelta(days=anchor.weekday())
    return monday, monday + timedelta(days=6)


def subject_distribution(sessions):
    """Count sessions per subject, most booked first.

    Returns ``(rows, peak)`` where rows is a list of ``(subject, count)``
    and peak is the largest count, so a template can size bars without
    recomputing anything.
    """
    counts = {}
    for s in sessions:
        counts[s.subject] = counts.get(s.subject, 0) + 1
    rows = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
    return rows, max(counts.values(), default=0)


@bp.route("/")
def dashboard():
    today = date.today()
    try:
        anchor = date.fromisoformat(request.args.get("week", ""))
    except ValueError:
        anchor = today
    monday, sunday = week_bounds(anchor)

    # ST-1 / ST-2: roster sizes.
    active_tutors = Tutor.query.filter_by(is_active=True).count()
    active_students = Student.query.filter_by(is_active=True).count()

    # ST-3: bookings falling inside the displayed week. Cancelled sessions
    # are excluded so the count reflects lessons that will actually run.
    week_sessions = (Session.query
                     .filter(Session.session_date >= monday,
                             Session.session_date <= sunday,
                             Session.status != "cancelled")
                     .order_by(Session.session_date, Session.start_time)
                     .all())

    # ST-4: subject split of those bookings.
    subjects, peak = subject_distribution(week_sessions)

    return render_template(
        "stats/dashboard.html",
        monday=monday,
        sunday=sunday,
        is_current_week=(monday <= today <= sunday),
        active_tutors=active_tutors,
        active_students=active_students,
        week_total=len(week_sessions),
        subjects=subjects,
        peak=peak,
        prev_week=(monday - timedelta(days=7)).isoformat(),
        next_week=(monday + timedelta(days=7)).isoformat(),
    )
