"""Flask application factory.

Author: Charon (Technical Lead)
"""
import os

from flask import Flask, redirect, url_for

from .config import get_config
from .models import db
from .seed import seed_database


def create_app(config_name: str | None = None) -> Flask:
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object(get_config(config_name))

    os.makedirs(app.instance_path, exist_ok=True)
    db.init_app(app)

    # Register blueprints
    from .routes.tutors import bp as tutors_bp
    from .routes.students import bp as students_bp
    from .routes.bookings import bp as bookings_bp
    from .routes.timetable import bp as timetable_bp
    from .routes.stats import bp as stats_bp

    app.register_blueprint(tutors_bp, url_prefix="/tutors")
    app.register_blueprint(students_bp, url_prefix="/students")
    app.register_blueprint(bookings_bp, url_prefix="/bookings")
    app.register_blueprint(timetable_bp, url_prefix="/timetable")
    app.register_blueprint(stats_bp, url_prefix="/stats")

    @app.route("/")
    def index():
        return redirect(url_for("stats.dashboard"))

    @app.cli.command("seed-db")
    def seed_db_command():
        """Create tables and insert demo data."""
        db.create_all()
        seed_database()

    with app.app_context():
        db.create_all()

    return app
