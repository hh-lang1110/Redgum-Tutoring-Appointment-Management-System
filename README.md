# Redgum Tutoring Appointment Management System

A small internal web application for Redgum Tutoring, an after-school tutoring centre in
Ipswich, QLD. It replaces the paper diary and whiteboard with a single weekly schedule.

## Scope (per case study)

- **Students**: create, find, update, make inactive.
- **Tutors**: create, find, update, deactivate; maintain weekly **availability windows**.
- **Sessions**: book one student with one tutor on a date/time; status lifecycle
  (booked -> attended / cancelled / missed); move and cancel.
- **Core rule**: a session may only be booked entirely inside one of the tutor's
  availability windows for that weekday.
- **Rooms**: each session records the room it occupies; a room cannot host two
  overlapping sessions, and neither can a tutor.
- **Subject matching**: a session must be in a subject the tutor teaches and the
  student is enrolled in.
- **Views**: weekly schedule (filterable by tutor, student or room), a tutor's own
  upcoming sessions, a student's session history, and a statistics dashboard.

Explicitly out of scope: invoicing, payments, notifications, parent portal,
blue-card tracking.

## Tech stack

Python 3.12 + Flask 3 + Flask-SQLAlchemy + Bootstrap 5 (CDN) + SQLite (dev) /
PostgreSQL (prod). Deployable via Dockerfile or Render Procfile.

## Run from a clean checkout

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # Windows: copy .env.example .env
flask db upgrade              # create/update the schema
flask seed-db                 # optional: insert demo data (also migrates)
python run.py
```

Open http://127.0.0.1:5000/

## Database migrations

The schema is owned by Alembic migrations under `migrations/`. The application
never creates tables itself outside the test suite, because
`db.create_all()` only adds *missing tables* and silently ignores new
*columns* on a table that already exists - which is exactly the kind of drift
that went unnoticed in the prototype.

```bash
flask db upgrade                        # apply pending migrations
flask db migrate -m "add X to Y"        # generate a migration from model changes
flask db downgrade                      # roll back one revision
flask db current                        # show the revision the DB is on
```

Always read a generated migration before committing it; Alembic does not detect
column renames and will emit a drop plus an add, which loses data.

### If you have a database from before migrations existed

The baseline migration (`initial schema`) creates every table from scratch, so
it cannot be applied on top of a database that already has them - `flask db
upgrade` will stop with `table students already exists`. Such a database also
predates the `room`, `qualification`, `email` and `parent_name` columns, so
stamping it as current would be wrong. Delete it and rebuild:

```bash
rm instance/redgum.sqlite3     # Windows: del instance\redgum.sqlite3
flask db upgrade && flask seed-db
```

## Project layout

```
app/
  __init__.py        # application factory, blueprint registration, error pages
  config.py          # Development / Testing / Production config classes
  models.py          # Tutor, TutorAvailability, Student, Session
  validation.py      # field-length and availability-window validation
  seed.py            # demo data (case study Documents A & B)
  routes/
    _util.py         # safe_redirect_target
    tutors.py        # CRUD + availability window management
    students.py      # CRUD + session history
    sessions.py      # book, move, set status, tutor's own view
    schedule.py      # weekly view + tutor/student/room filters
    stats.py         # statistics dashboard
  templates/
migrations/          # Alembic revisions; owns the schema
tests/               # pytest suite
docs/                # requirements specification
```

## Testing

```bash
pip install -r requirements-dev.txt
pytest          # 101 tests
ruff check .    # lint
```

## Branching

Work is done on short-lived branches merged with `--no-ff`, so the history
records where each change came from.

- `main` - release v1.0.0
- `feature/vivian-requirements` - requirements & data model
- `feature/charon-technical` - Flask app, config, deployment, CI
- `feature/eva-project-integration` - README, CHANGELOG, CI

Branches used to bring v1.0.0 to its released state:
`fix/environment-config-guards`, `feature/data-model-completion`,
`feature/booking-validation`, `feature/statistics-dashboard`,
`feature/timetable-filters`, `build/database-migrations`, `build/quality-and-ci`,
`docs/align-with-implementation`.
