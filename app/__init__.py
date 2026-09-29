"""Flask application factory."""
import os
from flask import Flask, redirect, url_for
from flask_migrate import Migrate, upgrade
from .config import get_config
from .models import db
from .seed import seed_database

# SQLite cannot ALTER or DROP a column in place, so Alembic has to rebuild the
# table for those operations. Batch mode makes it emit that rebuild instead of
# generating SQL the database will reject.
migrate = Migrate(render_as_batch=True)


def create_app(config_name=None):
    config_class = get_config(config_name)
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object(config_class)
    # from_object() only copies uppercase attributes; it never calls init_app,
    # so every per-environment guard stays dormant unless we invoke it here.
    config_class.init_app(app)
    os.makedirs(app.instance_path, exist_ok=True)
    db.init_app(app)
    migrate.init_app(app, db)

    from .routes.tutors import bp as tutors_bp
    from .routes.students import bp as students_bp
    from .routes.sessions import bp as sessions_bp
    from .routes.schedule import bp as schedule_bp
    from .routes.stats import bp as stats_bp

    app.register_blueprint(tutors_bp, url_prefix="/tutors")
    app.register_blueprint(students_bp, url_prefix="/students")
    app.register_blueprint(sessions_bp, url_prefix="/sessions")
    app.register_blueprint(schedule_bp, url_prefix="/schedule")
    app.register_blueprint(stats_bp, url_prefix="/stats")

    @app.route("/")
    def index():
        return redirect(url_for("schedule.weekly"))

    @app.cli.command("seed-db")
    def seed_db_command():
        """Bring the schema up to date, then load the demo data."""
        upgrade()
        seed_database()

    if app.config.get("AUTO_CREATE_SCHEMA"):
        with app.app_context():
            db.create_all()
    return app
