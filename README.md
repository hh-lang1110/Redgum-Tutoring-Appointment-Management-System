# Redgum Tutoring Appointment Management System

A lightweight internal web application for Redgum Tutoring (single centre) to
digitise tutor and student records, manage lesson bookings, view the weekly
timetable and produce basic operational statistics.

Built for ISYS3001 Assessment 2 — Software Configuration & Procurement Management.

## Features

- **Tutor profiles** — name, subjects, qualification, contact, availability; soft-delete.
- **Student profiles** — name, grade, parent contact, enrolled subjects; soft-delete.
- **Lesson booking** — tutor–student pairing with automatic **tutor** and **room** conflict detection.
- **Weekly timetable** — Mon–Sat grid (09:00–20:00), filterable by tutor / student / room.
- **Statistics dashboard** — active tutors, active students, weekly bookings, subject distribution.

## Tech stack

| Layer | Choice |
|---|---|
| Language | Python 3.11+ |
| Web framework | Flask 3 |
| ORM | Flask-SQLAlchemy |
| Database | SQLite (dev) / PostgreSQL (prod via `DATABASE_URL`) |
| Frontend | Server-rendered Jinja2 templates + Bootstrap 5 (CDN) |
| WSGI server | Gunicorn |
| Container | Dockerfile |
| PaaS deploy | Render (`Procfile`) |
| CI | GitHub Actions |

## Project structure

```
app/
  __init__.py        # Flask app factory
  config.py          # Dev / Testing / Production config classes
  models.py          # Tutor, Student, Booking
  seed.py            # Demo data
  routes/            # tutors, students, bookings, timetable, stats
  templates/         # Jinja2 pages
  static/css/        # Custom styles
docs/
  requirements.md    # Functional and non-functional requirements
.github/
  workflows/ci.yml    # CI pipeline
.env.example         # Template for local environment
Dockerfile
Procfile
requirements.txt
run.py               # gunicorn entry point
```

## Configuration management

All environment-specific values are read from environment variables (see
`.env.example`). Three configuration classes in `app/config.py` target
`development`, `testing` and `production`; production refuses to start with the
default `SECRET_KEY`.

## Quick start (local)

```bash
python -m venv .venv
. .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # then edit .env if needed
flask --app run.py seed-db   # create tables and insert demo data
flask --app run.py --debug run
# open http://127.0.0.1:5000
```

## Branching strategy

- `main` — production-ready, protected.
- `feature/vivian-requirements` — requirements spec, data models, seed data.
- `feature/charon-technical` — application code, deployment config.
- `feature/eva-project-integration` — README, CHANGELOG, CI, final merge.

Each feature branch is merged into `main` through a pull request. Commit
messages follow Conventional Commits (`feat:`, `fix:`, `chore:`, `docs:`).

## Team

| Role | Person | Branch |
|---|---|---|
| Project Manager / Integration | Eva (Liu) | `feature/eva-project-integration` |
| Technical Lead | Charon (Han) | `feature/charon-technical` |
| Business & Requirements | Vivian (Ke) | `feature/vivian-requirements` |

## License

Academic project — not for redistribution.
