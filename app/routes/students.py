"""Student profiles."""
from flask import Blueprint, flash, redirect, render_template, request, url_for

from ..models import Session, Student, db
from ..validation import length_errors

bp = Blueprint("students", __name__, url_prefix="/students")

FIELDS = ("name", "year_level", "parent_name", "parent_phone",
          "parent_email", "enrolled_subjects")


def _form_values(student=None):
    """Read the student form, keeping stored values for absent fields."""
    def field(name):
        default = getattr(student, name, "") if student is not None else ""
        return request.form.get(name, default or "").strip()

    return {name: field(name) for name in FIELDS}


@bp.route("/")
def list_students():
    students = Student.query.order_by(Student.is_active.desc(), Student.name).all()
    return render_template("students/list.html", students=students)


@bp.route("/new", methods=["GET", "POST"])
def new_student():
    if request.method == "POST":
        values = _form_values()
        errors = length_errors(values)
        if not values["name"]:
            errors.append("Student name is required.")
        if errors:
            for message in errors:
                flash(message, "danger")
            return render_template("students/form.html", student=values)
        s = Student(**values)
        db.session.add(s)
        db.session.commit()
        flash(f"Student {s.name} added.", "success")
        return redirect(url_for("students.list_students"))
    return render_template("students/form.html", student={})


@bp.route("/<int:student_id>", methods=["GET", "POST"])
def edit_student(student_id):
    s = db.get_or_404(Student, student_id)
    if request.method == "POST":
        values = _form_values(s)
        errors = length_errors(values)
        if errors:
            for message in errors:
                flash(message, "danger")
            return render_template("students/form.html", student=s)
        s.name = values["name"] or s.name
        s.year_level = values["year_level"]
        s.parent_name = values["parent_name"]
        s.parent_phone = values["parent_phone"]
        s.parent_email = values["parent_email"]
        s.enrolled_subjects = values["enrolled_subjects"]
        if request.form.get("deactivate"):
            s.is_active = False
            flash(f"{s.name} made inactive (past sessions kept).", "warning")
        elif request.form.get("reactivate"):
            s.is_active = True
            flash(f"{s.name} reactivated.", "success")
        db.session.commit()
        return redirect(url_for("students.list_students"))
    return render_template("students/form.html", student=s)


@bp.route("/<int:student_id>/sessions")
def student_sessions(student_id):
    s = db.get_or_404(Student, student_id)
    sessions = (s.sessions.order_by(db.desc(Session.session_date),
                                   db.desc(Session.start_time)).all())
    return render_template("students/sessions.html", student=s, sessions=sessions)


