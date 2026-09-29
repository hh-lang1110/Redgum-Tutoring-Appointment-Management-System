"""Sessions: create, move, cancel, mark attended/missed, tutor's own view."""
from datetime import date, datetime

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

from ..models import SESSION_STATUSES, Session, Student, Tutor, db
from ..validation import length_errors
from ._util import safe_redirect_target

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
        notes = request.form.get("notes", "").strip()
        errors = length_errors({"subject": subject, "room": room, "notes": notes})
        if not (tutor_id and student_id and subject and d and start_time and duration):
            errors.append("All fields are required.")
        if errors:
            for message in errors:
                flash(message, "danger")
            return render_template("sessions/form.html", tutors=tutors, students=students,
                                   form=request.form)
        # db.session.get is the SQLAlchemy 2.0 form; Model.query.get is legacy.
        tutor = db.session.get(Tutor, tutor_id)
        student = db.session.get(Student, student_id)
        if tutor is None or student is None:
            abort(404)

        # BR-4: the subject must be one the tutor teaches and one the student
        # is enrolled in, or the booking is meaningless.
        if not tutor.teaches(subject):
            flash(f"{tutor.name} is not listed to teach {subject}.", "danger")
            return render_template("sessions/form.html", tutors=tutors, students=students,
                                   form=request.form)
        if not student.enrolled_in(subject):
            flash(f"{student.name} is not enrolled in {subject}.", "danger")
            return render_template("sessions/form.html", tutors=tutors, students=students,
                                   form=request.form)

        ok, reason = tutor.can_fit(d.weekday(), start_time, duration)
        if not ok:
            flash(reason, "danger")
            return render_template("sessions/form.html", tutors=tutors, students=students,
                                   form=request.form)

        # BR-2 / BR-3: neither the tutor nor the room may be double-booked.
        clash, kind = Session.find_clash(tutor_id, d, start_time, duration, room)
        if clash is not None:
            busy = tutor.name if kind == "tutor" else room
            flash(f"{busy} is already booked "
                  f"{clash.start_time}-{clash.end_time()} on {clash.session_date}.", "danger")
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
    s = db.get_or_404(Session, sid)
    if request.method == "POST":
        d = _parse_date(request.form.get("session_date", ""))
        start_time = request.form.get("start_time", "").strip()
        duration = request.form.get("duration_minutes", s.duration_minutes, type=int)
        room = request.form.get("room", s.room or "").strip()
        errors = length_errors({"room": room})
        if not (d and start_time):
            errors.append("Date and start time are required.")
        if errors:
            for message in errors:
                flash(message, "danger")
        else:
            tutor = s.tutor
            ok, reason = tutor.can_fit(d.weekday(), start_time, duration)
            clash, kind = Session.find_clash(tutor.id, d, start_time, duration, room,
                                             exclude_id=s.id)
            if not ok:
                flash(reason, "danger")
            elif clash is not None:
                busy = tutor.name if kind == "tutor" else room
                flash(f"{busy} is already booked "
                      f"{clash.start_time}-{clash.end_time()} on {clash.session_date}.",
                      "danger")
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
    s = db.get_or_404(Session, sid)
    new_status = request.form.get("status", "")
    if new_status not in SESSION_STATUSES:
        abort(400)
    s.status = new_status
    db.session.commit()
    flash(f"Session marked as {new_status}.", "info")
    return redirect(safe_redirect_target(request.referrer,
                                         url_for("sessions.list_sessions")))


@bp.route("/tutor/<int:tutor_id>")
def tutor_sessions(tutor_id):
    tutor = db.get_or_404(Tutor, tutor_id)
    today = date.today()
    upcoming = (Session.query
                .filter(Session.tutor_id == tutor_id,
                        Session.session_date >= today,
                        Session.status == "booked")
                .order_by(Session.session_date, Session.start_time).all())
    return render_template("sessions/tutor_view.html", tutor=tutor, sessions=upcoming)

