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
- **Views**: weekly schedule, a tutor's own upcoming sessions, a student's session history.

Explicitly out of scope: room allocation, double-booking detection, invoicing,
payments, notifications, parent portal, blue-card tracking.

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
  __init__.py        # application factory
  config.py          # Development / Testing / Production config classes
  models.py          # Tutor, TutorAvailability, Student, Session
  seed.py            # demo data (case study Documents A & B)
  routes/
    tutors.py        # CRUD + availability window management
    students.py      # CRUD + session history
    sessions.py      # book, move, set status, tutor's own view
    schedule.py      # weekly view
tests/smoke_test.py  # CI smoke test
```

## Branching

- `main` - release v1.0.0
- `feature/ke-requirements` - requirements & data model
- `feature/han-technical` - Flask app, config, deployment, CI
- `feature/liu-project-integration` - README, CHANGELOG, CI
