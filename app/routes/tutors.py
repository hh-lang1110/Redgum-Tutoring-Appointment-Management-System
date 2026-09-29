"""Tutor profiles and availability windows."""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from ..models import db, Tutor, TutorAvailability, WEEKDAY_NAMES

bp = Blueprint("tutors", __name__, url_prefix="/tutors")


@bp.route("/")
def list_tutors():
    tutors = Tutor.query.order_by(Tutor.is_active.desc(), Tutor.name).all()
    return render_template("tutors/list.html", tutors=tutors)


@bp.route("/new", methods=["GET", "POST"])
def new_tutor():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        subjects = request.form.get("subjects", "").strip()
        qualification = request.form.get("qualification", "").strip()
        phone = request.form.get("phone", "").strip()
        email = request.form.get("email", "").strip()
        if not name or not subjects:
            flash("Name and subjects are required.", "danger")
            return render_template("tutors/form.html", tutor={})
        t = Tutor(name=name, subjects=subjects, qualification=qualification,
                  phone=phone, email=email)
        db.session.add(t)
        db.session.commit()
        flash(f"Tutor {name} created. Add their availability next.", "success")
        return redirect(url_for("tutors.edit_tutor", tutor_id=t.id))
    return render_template("tutors/form.html", tutor={})


@bp.route("/<int:tutor_id>", methods=["GET", "POST"])
def edit_tutor(tutor_id):
    t = Tutor.query.get_or_404(tutor_id)
    if request.method == "POST":
        t.name = request.form.get("name", t.name).strip() or t.name
        t.subjects = request.form.get("subjects", t.subjects).strip() or t.subjects
        t.qualification = request.form.get("qualification", t.qualification).strip()
        t.phone = request.form.get("phone", t.phone).strip()
        t.email = request.form.get("email", t.email).strip()
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
    t = Tutor.query.get_or_404(tutor_id)
    try:
        dow = int(request.form.get("day_of_week", -1))
        start = request.form.get("start_time", "").strip()
        end = request.form.get("end_time", "").strip()
        if not (0 <= dow <= 6) or not start or not end:
            raise ValueError
        w = TutorAvailability(tutor_id=t.id, day_of_week=dow,
                              start_time=start, end_time=end)
        db.session.add(w)
        db.session.commit()
        flash(f"Availability added: {WEEKDAY_NAMES[dow]} {start}-{end}.", "success")
    except Exception:
        flash("Invalid availability window.", "danger")
    return redirect(url_for("tutors.edit_tutor", tutor_id=t.id))


@bp.route("/availability/<int:win_id>/delete", methods=["POST"])
def delete_availability(win_id):
    w = TutorAvailability.query.get_or_404(win_id)
    tid = w.tutor_id
    db.session.delete(w)
    db.session.commit()
    flash("Availability window removed.", "info")
    return redirect(url_for("tutors.edit_tutor", tutor_id=tid))

