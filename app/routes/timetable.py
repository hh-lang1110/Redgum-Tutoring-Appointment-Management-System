"""Weekly timetable view.

Author: Charon (Technical Lead)
"""
from flask import Blueprint, render_template, request

from ..models import Booking, Student, Tutor

bp = Blueprint("timetable", __name__)

DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]


@bp.route("/")
def weekly():
    tutors = Tutor.query.order_by(Tutor.name).all()
    students = Student.query.order_by(Student.name).all()

    tutor_id = request.args.get("tutor_id", type=int)
    student_id = request.args.get("student_id", type=int)
    room = request.args.get("room", "").strip()

    q = Booking.query.filter_by(is_cancelled=False)
    if tutor_id:
        q = q.filter_by(tutor_id=tutor_id)
    if student_id:
        q = q.filter_by(student_id=student_id)
    if room:
        q = q.filter(Booking.room.ilike(f"%{room}%"))

    bookings = q.all()

    # Build grid: rows = hour buckets 9..20, cols = 6 days
    grid = [[[] for _ in range(len(DAYS))] for _ in range(12)]
    for b in bookings:
        try:
            hour = int(b.start_time.split(":")[0])
        except Exception:
            continue
        row = hour - 9
        if 0 <= row < 12 and 0 <= b.weekday < 6:
            grid[row][b.weekday].append(b)

    rooms = sorted({b.room for b in Booking.query.all() if b.room})

    return render_template(
        "timetable/weekly.html",
        grid=grid, days=DAYS, tutors=tutors, students=students, rooms=rooms,
        filter_tutor_id=tutor_id, filter_student_id=student_id, filter_room=room,
    )
