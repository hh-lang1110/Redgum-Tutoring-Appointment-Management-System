"""Tutor profile routes.

Author: Charon (Technical Lead)
"""
from flask import Blueprint, flash, redirect, render_template, request, url_for

from ..models import Tutor, db

bp = Blueprint("tutors", __name__)


@bp.route("/")
def list_tutors():
    tutors = Tutor.query.order_by(Tutor.name).all()
    return render_template("tutors/list.html", tutors=tutors)


@bp.route("/new", methods=["GET", "POST"])
def create_tutor():
    if request.method == "POST":
        t = Tutor(
            name=request.form["name"].strip(),
            subjects=request.form["subjects"].strip(),
            qualification=request.form.get("qualification", "").strip(),
            phone=request.form.get("phone", "").strip(),
            email=request.form.get("email", "").strip(),
            availability_note=request.form.get("availability_note", "").strip(),
        )
        if not t.name or not t.subjects:
            flash("Name and at least one subject are required.", "danger")
        else:
            db.session.add(t)
            db.session.commit()
            flash("Tutor added.", "success")
            return redirect(url_for("tutors.list_tutors"))
    return render_template("tutors/form.html", tutor=None)


@bp.route("/<int:tutor_id>/edit", methods=["GET", "POST"])
def edit_tutor(tutor_id):
    t = Tutor.query.get_or_404(tutor_id)
    if request.method == "POST":
        t.name = request.form["name"].strip()
        t.subjects = request.form["subjects"].strip()
        t.qualification = request.form.get("qualification", "").strip()
        t.phone = request.form.get("phone", "").strip()
        t.email = request.form.get("email", "").strip()
        t.availability_note = request.form.get("availability_note", "").strip()
        t.is_active = bool(request.form.get("is_active"))
        db.session.commit()
        flash("Tutor updated.", "success")
        return redirect(url_for("tutors.list_tutors"))
    return render_template("tutors/form.html", tutor=t)
