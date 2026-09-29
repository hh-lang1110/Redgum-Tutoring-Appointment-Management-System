"""Student profiles."""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from ..models import db, Session, Student

bp = Blueprint("students", __name__, url_prefix="/students")


@bp.route("/")
def list_students():
    students = Student.query.order_by(Student.is_active.desc(), Student.name).all()
    return render_template("students/list.html", students=students)


@bp.route("/new", methods=["GET", "POST"])
def new_student():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        year_level = request.form.get("year_level", "").strip()
        parent_name = request.form.get("parent_name", "").strip()
        parent_phone = request.form.get("parent_phone", "").strip()
        parent_email = request.form.get("parent_email", "").strip()
        enrolled = request.form.get("enrolled_subjects", "").strip()
        if not name:
            flash("Student name is required.", "danger")
            return render_template("students/form.html", student={})
        s = Student(name=name, year_level=year_level, parent_name=parent_name,
                    parent_phone=parent_phone, parent_email=parent_email,
                    enrolled_subjects=enrolled)
        db.session.add(s)
        db.session.commit()
        flash(f"Student {name} added.", "success")
        return redirect(url_for("students.list_students"))
    return render_template("students/form.html", student={})


@bp.route("/<int:student_id>", methods=["GET", "POST"])
def edit_student(student_id):
    s = Student.query.get_or_404(student_id)
    if request.method == "POST":
        s.name = request.form.get("name", s.name).strip() or s.name
        s.year_level = request.form.get("year_level", s.year_level).strip()
        s.parent_name = request.form.get("parent_name", s.parent_name).strip()
        s.parent_phone = request.form.get("parent_phone", s.parent_phone).strip()
        s.parent_email = request.form.get("parent_email", s.parent_email).strip()
        s.enrolled_subjects = request.form.get("enrolled_subjects", s.enrolled_subjects).strip()
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
    s = Student.query.get_or_404(student_id)
    sessions = (s.sessions.order_by(db.desc(Session.session_date),
                                   db.desc(Session.start_time)).all())
    return render_template("students/sessions.html", student=s, sessions=sessions)


