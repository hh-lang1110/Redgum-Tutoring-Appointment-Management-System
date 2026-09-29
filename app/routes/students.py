"""Student profile routes.

Author: Charon (Technical Lead)
"""
from flask import Blueprint, flash, redirect, render_template, request, url_for

from ..models import Student, db

bp = Blueprint("students", __name__)


@bp.route("/")
def list_students():
    students = Student.query.order_by(Student.name).all()
    return render_template("students/list.html", students=students)


@bp.route("/new", methods=["GET", "POST"])
def create_student():
    if request.method == "POST":
        s = Student(
            name=request.form["name"].strip(),
            grade_level=request.form.get("grade_level", "").strip(),
            parent_name=request.form.get("parent_name", "").strip(),
            parent_phone=request.form.get("parent_phone", "").strip(),
            parent_email=request.form.get("parent_email", "").strip(),
            enrolled_subjects=request.form.get("enrolled_subjects", "").strip(),
        )
        if not s.name:
            flash("Student name is required.", "danger")
        else:
            db.session.add(s)
            db.session.commit()
            flash("Student added.", "success")
            return redirect(url_for("students.list_students"))
    return render_template("students/form.html", student=None)


@bp.route("/<int:student_id>/edit", methods=["GET", "POST"])
def edit_student(student_id):
    s = Student.query.get_or_404(student_id)
    if request.method == "POST":
        s.name = request.form["name"].strip()
        s.grade_level = request.form.get("grade_level", "").strip()
        s.parent_name = request.form.get("parent_name", "").strip()
        s.parent_phone = request.form.get("parent_phone", "").strip()
        s.parent_email = request.form.get("parent_email", "").strip()
        s.enrolled_subjects = request.form.get("enrolled_subjects", "").strip()
        s.is_active = bool(request.form.get("is_active"))
        db.session.commit()
        flash("Student updated.", "success")
        return redirect(url_for("students.list_students"))
    return render_template("students/form.html", student=s)
