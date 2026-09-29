"""Tutor profiles and availability windows."""
from flask import Blueprint, flash, redirect, render_template, request, url_for

from ..models import WEEKDAY_NAMES, Tutor, TutorAvailability, db
from ..validation import length_errors, window_error

bp = Blueprint("tutors", __name__, url_prefix="/tutors")


@bp.route("/")
def list_tutors():
    tutors = Tutor.query.order_by(Tutor.is_active.desc(), Tutor.name).all()
    return render_template("tutors/list.html", tutors=tutors)


def _form_values(tutor=None):
    """Read the tutor form, falling back to the stored record when editing.

    A field that is absent from the submission keeps its stored value rather
    than clearing it, so a partial POST cannot wipe the contact details.
    """
    def field(name):
        default = getattr(tutor, name, "") if tutor is not None else ""
        return request.form.get(name, default or "").strip()

    return {name: field(name)
            for name in ("name", "subjects", "qualification", "phone", "email")}


@bp.route("/new", methods=["GET", "POST"])
def new_tutor():
    if request.method == "POST":
        values = _form_values()
        errors = length_errors(values)
        if not values["name"] or not values["subjects"]:
            errors.append("Name and subjects are required.")
        if errors:
            for message in errors:
                flash(message, "danger")
            return render_template("tutors/form.html", tutor=values)
        t = Tutor(**values)
        db.session.add(t)
        db.session.commit()
        flash(f"Tutor {t.name} created. Add their availability next.", "success")
        return redirect(url_for("tutors.edit_tutor", tutor_id=t.id))
    return render_template("tutors/form.html", tutor={})


@bp.route("/<int:tutor_id>", methods=["GET", "POST"])
def edit_tutor(tutor_id):
    t = db.get_or_404(Tutor, tutor_id)
    if request.method == "POST":
        values = _form_values(t)
        errors = length_errors(values)
        if errors:
            for message in errors:
                flash(message, "danger")
            return render_template("tutors/form.html", tutor=t, weekdays=WEEKDAY_NAMES)
        t.name = values["name"] or t.name
        t.subjects = values["subjects"] or t.subjects
        t.qualification = values["qualification"]
        t.phone = values["phone"]
        t.email = values["email"]
        if request.form.get("deactivate"):
            t.is_active = False
            flash(f"{t.name} deactivated (past sessions are kept).", "warning")
        elif request.form.get("reactivate"):
            t.is_active = True
            flash(f"{t.name} reactivated.", "success")
        db.session.commit()
        return redirect(url_for("tutors.list_tutors"))
    return render_template("tutors/form.html", tutor=t, weekdays=WEEKDAY_NAMES)


@bp.route("/<int:tutor_id>/availability/add", methods=["POST"])
def add_availability(tutor_id):
    t = db.get_or_404(Tutor, tutor_id)
    start = request.form.get("start_time", "").strip()
    end = request.form.get("end_time", "").strip()
    try:
        dow = int(request.form.get("day_of_week", -1))
    except (TypeError, ValueError):
        dow = -1
    if not 0 <= dow <= 6:
        flash("Choose a weekday for the availability window.", "danger")
        return redirect(url_for("tutors.edit_tutor", tutor_id=t.id))

    # Only same-day windows can overlap, so that is all we compare against.
    problem = window_error(start, end, t.windows_for(dow))
    if problem:
        flash(problem, "danger")
        return redirect(url_for("tutors.edit_tutor", tutor_id=t.id))

    db.session.add(TutorAvailability(tutor_id=t.id, day_of_week=dow,
                                     start_time=start, end_time=end))
    db.session.commit()
    flash(f"Availability added: {WEEKDAY_NAMES[dow]} {start}-{end}.", "success")
    return redirect(url_for("tutors.edit_tutor", tutor_id=t.id))


@bp.route("/availability/<int:win_id>/delete", methods=["POST"])
def delete_availability(win_id):
    w = db.get_or_404(TutorAvailability, win_id)
    tid = w.tutor_id
    db.session.delete(w)
    db.session.commit()
    flash("Availability window removed.", "info")
    return redirect(url_for("tutors.edit_tutor", tutor_id=tid))
