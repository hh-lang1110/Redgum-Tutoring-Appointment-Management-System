"""Sessions: create, move, cancel, mark attended/missed, tutor's own view."""
from datetime import date, datetime, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from ..models import db, Session, Tutor, Student, SESSION_STATUSES

bp = Blueprint("sessions", __name__, url_prefix="/sessions")


def _parse_date(value):
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except Exception:
        return None


@bp.route("/")
def list_sessions():
    date_filter = request.args.get("date", "")
    q = Session.query
    if date_filter:
        d = _parse_date(date_filter)
        if d:
            q = q.filter(Session.session_date == d)
    sessions = q.order_by(Session.session_date, Session.start_time).all()
    today = date.today().isoformat()
    return render_template("sessions/list.html", sessions=sessions,
                           date_filter=date_filter, today=today)


@bp.route("/new", methods=["GET", "POST"])
def new_session():
    tutors = Tutor.query.filter_by(is_active=True).order_by(Tutor.name).all()
    students = Student.query.filter_by(is_active=True).order_by(Student.name).all()
    if request.method == "POST":
        tutor_id = request.form.get("tutor_id", type=int)
        student_id = request.form.get("student_id", type=int)
        subject = request.form.get("subject", "").strip()
        d = _parse_date(request.form.get("session_date", ""))
        start_time = request.form.get("start_time", "").strip()
        duration = request.form.get("duration_minutes", 60, type=int)
        room = request.form.get("room", "").strip()
        if not (tutor_id and student_id and subject and d and start_time and duration):
            flash("All fields are required.", "danger")
            return render_template("sessions/form.html", tutors=tutors, students=students)
        tutor = Tutor.query.get(tutor_id)
        ok, reason = tutor.can_fit(d.weekday(), start_time, duration)
        if not ok:
            flash(reason, "danger")
            return render_template("sessions/form.html", tutors=tutors, students=students,
                                   form=request.form)
        s = Session(tutor_id=tutor_id, student_id=student_id, subject=subject,
                    session_date=d, start_time=start_time, duration_minutes=duration,
                    room=room, status="booked")
        db.session.add(s)
        db.session.commit()
        flash(f"Session booked: {tutor.name} with student on {d}.", "success")
        return redirect(url_for("sessions.list_sessions"))
    return render_template("sessions/form.html", tutors=tutors, students=students, form={})


@bp.route("/<int:sid>/move", methods=["GET", "POST"])
def move_session(sid):
    s = Session.query.get_or_404(sid)
    if request.method == "POST":
        d = _parse_date(request.form.get("session_date", ""))
        start_time = request.form.get("start_time", "").strip()
        duration = request.form.get("duration_minutes", s.duration_minutes, type=int)
        room = request.form.get("room", s.room).strip()
        if not (d and start_time):
            flash("Date and start time are required.", "danger")
        else:
            tutor = s.tutor
            ok, reason = tutor.can_fit(d.weekday(), start_time, duration)
            if not ok:
                flash(reason, "danger")
            else:
                s.session_date = d
                s.start_time = start_time
                s.duration_minutes = duration
                s.room = room
                db.session.commit()
                flash("Session moved.", "success")
                return redirect(url_for("sessions.list_sessions"))
    return render_template("sessions/move.html", s=s)


@bp.route("/<int:sid>/status", methods=["POST"])
def set_status(sid):
    s = Session.query.get_or_404(sid)
    new_status = request.form.get("status", "")
    if new_status not in SESSION_STATUSES:
        abort(400)
    s.status = new_status
    db.session.commit()
    flash(f"Session marked as {new_status}.", "info")
    return redirect(request.referrer or url_for("sessions.list_sessions"))


@bp.route("/tutor/<int:tutor_id>")
def tutor_sessions(tutor_id):
    tutor = Tutor.query.get_or_404(tutor_id)
    today = date.today()
    upcoming = (Session.query
                .filter(Session.tutor_id == tutor_id,
                        Session.session_date >= today,
                        Session.status == "booked")
                .order_by(Session.session_date, Session.start_time).all())
    return render_template("sessions/tutor_view.html", tutor=tutor, sessions=upcoming)

