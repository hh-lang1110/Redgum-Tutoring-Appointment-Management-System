"""Week schedule view (Mon-Sat) with optional tutor / student / room filters."""
from datetime import date, timedelta

from flask import Blueprint, render_template, request
from sqlalchemy import func

from ..models import WEEKDAY_NAMES, Session, Student, Tutor, db

bp = Blueprint("schedule", __name__, url_prefix="/schedule")


def _monday(d):
    return d - timedelta(days=d.weekday())


def _filter_args():
    """Read the TT-2 filter parameters off the querystring.

    Returns ``(filters, tutor_id, student_id, room)`` where ``filters`` holds
    only the values actually supplied, so it can be splatted back into
    ``url_for`` to carry the current view across week navigation.
    """
    tutor_id = request.args.get("tutor", type=int)
    student_id = request.args.get("student", type=int)
    room = request.args.get("room", "").strip()

    filters = {}
    if tutor_id:
        filters["tutor"] = tutor_id
    if student_id:
        filters["student"] = student_id
    if room:
        filters["room"] = room
    return filters, tutor_id, student_id, room


@bp.route("/")
def weekly():
    week_param = request.args.get("week", "")
    try:
        base = date.fromisoformat(week_param)
    except Exception:
        base = date.today()
    monday = _monday(base)
    days = [monday + timedelta(days=i) for i in range(6)]  # Mon..Sat

    filters, tutor_id, student_id, room = _filter_args()

    rows = []
    for d in days:
        q = Session.query.filter(Session.session_date == d,
                                 Session.status != "cancelled")
        # TT-2: narrow the grid down to one tutor, one student or one room.
        if tutor_id:
            q = q.filter(Session.tutor_id == tutor_id)
        if student_id:
            q = q.filter(Session.student_id == student_id)
        if room:
            # Room labels are free text, so match case-insensitively to keep
            # "room 2" and "Room 2" pointing at the same slot.
            q = q.filter(func.lower(Session.room) == room.lower())
        rows.append((d, WEEKDAY_NAMES[d.weekday()], q.order_by(Session.start_time).all()))

    return render_template(
        "schedule/weekly.html",
        rows=rows,
        monday=monday,
        prev_week=(monday - timedelta(days=7)).isoformat(),
        next_week=(monday + timedelta(days=7)).isoformat(),
        filters=filters,
        tutor_id=tutor_id,
        student_id=student_id,
        room=room,
        tutors=Tutor.query.filter_by(is_active=True).order_by(Tutor.name).all(),
        students=Student.query.filter_by(is_active=True).order_by(Student.name).all(),
        rooms=[r for (r,) in db.session.query(Session.room)
               .filter(Session.room.isnot(None), Session.room != "")
               .distinct().order_by(Session.room).all()],
        total=sum(len(sessions) for _, _, sessions in rows),
    )
