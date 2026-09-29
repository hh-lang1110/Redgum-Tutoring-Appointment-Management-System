# Changelog

All notable changes to this project are documented here.
Format based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [1.0.0] — 2026-09-29

First release in which the code, the requirements specification and this
file agree with one another. See [Origin](#origin) for what the starting
point contained and what was wrong with it.

### Added

- Alembic migrations under `migrations/`, with a baseline revision that
  creates the full schema. The schema is no longer created by the
  application at start-up, so a column change can no longer be silently
  skipped on an existing database.
- `room` on sessions, with conflict detection for the room as well as the
  tutor (BR-2, BR-3), and for the tutor's remaining profile fields
  (qualification, email) and the student's parent email.
- Subject matching (BR-4): a booking is refused unless the tutor teaches
  the subject and the student is enrolled in it.
- Timetable filters by tutor, by student and by room, carried across week
  navigation (TT-2).
- Statistics dashboard at `/stats/`: active tutors, active students,
  bookings in the displayed week and the subject split of those bookings
  (ST-1 to ST-4).
- Length validation matching the column widths in `models.py`, so values
  that SQLite accepts are not rejected later by PostgreSQL.
- Validation of availability windows: times must parse, a window must end
  after it starts, and it may not overlap another window on the same day.
- Friendly 404 and 500 pages; the 500 handler rolls the session back
  first.
- A test suite of 101 tests covering the domain rules both in isolation
  and through the HTTP endpoints, plus roster CRUD, validation, error
  handling and the redirect guard.
- `ruff` configuration in `pyproject.toml`, with `pyupgrade` and `bugbear`
  enabled.
- CI that lints and runs the suite on Python 3.11 and 3.12, and a second
  job that proves the migrations build the schema, apply idempotently,
  match the models with no drift, and reverse cleanly.
- `.dockerignore`, a non-root container user, a container healthcheck, and
  `docker-compose.yml` running against PostgreSQL for local parity with
  production.
- The missing `psycopg2` driver: the documented production
  `DATABASE_URL=postgresql://...` could not have connected without it.
- `LICENSE`, `CONTRIBUTING.md` and a pull request template.

### Changed

- Configuration guards are now actually executed. `Config.from_object`
  only copies uppercase attributes and never calls `init_app`, so the
  production `SECRET_KEY` check had been unreachable dead code.
- `flask seed-db` brings the schema up to date before loading demo data,
  so one command still takes a clean checkout to a working demo.
- Deployment runs `flask db upgrade` on release instead of seeding.

### Fixed

- A session could be given a negative duration, which the form's
  `min="30"` did not prevent: the value was only checked for truthiness.
  Because every time-based rule compares a start against an end, such a
  session also passed the availability check and never registered as a
  clash, so it could be booked on top of an existing lesson without the
  conflict check firing. Durations are now bounded to 30-480 minutes, on
  both the booking and the move endpoints.
- A session could be booked on a Sunday. It was stored and counted by the
  statistics dashboard but never appeared in the weekly timetable, which
  covers Monday to Saturday. Availability could also be recorded for
  Sunday. The bookable range is now enforced consistently.
- A pre-existing database created by the old `db.create_all()` was missing
  every column added afterwards and would fail with
  `no such column: sessions.room` with nothing pointing at the cause.
- `datetime.utcnow()` replaced (deprecated in Python 3.12, and it returns
  a naive value that reads as local time).
- SQLAlchemy 1.x `Model.query.get()` and `query.get_or_404()` calls
  replaced with the 2.0 forms.
- The Procfile release phase ran `flask seed-db`, which would have inserted
  the demo tutors and students into the production database. It also
  swallowed migration failures with `|| true`, so a failed migration would
  have started the new code against the old schema.

### Security

- The session status endpoint no longer redirects to an unchecked
  `Referer` header, which had made it an open redirect.
- `ProductionConfig` refuses to start when `SECRET_KEY` is unset or still
  the placeholder that is public in this repository.

## Origin

This release branches from the team repository's `main` at the commit
`refactor: align domain model with case study`, which is the shared
starting point. Everything below describes that branch point, so a reader
can tell what this release added from what it inherited.

The inherited tree contradicted its own documentation:

- `docs/requirements.md` still specifies a statistics dashboard
  (ST-1 to ST-4), but `app/routes/stats.py` and its template were removed
  by that refactor, so nothing implemented the requirement.
- The same document specified a `Booking` model; the code had settled on
  `Session`, with different field names.
- There were no migrations. The schema came from `db.create_all()`, which
  cannot add a column to an existing table, so an installed database
  drifted from the models with no error until a query touched the
  missing column.
- `ProductionConfig.init_app` was dead code that Flask never invoked,
  because `Config.from_object` only copies uppercase attributes.
- `Procfile` released with `flask seed-db`, which would have inserted the
  demo tutors and students into the production database.
- The only automated check was `tests/smoke_test.py`, whose `main()` the
  pytest configuration never collected. CI in turn ran an import check
  only; the route tests were verified by hand.

Version 1.0.0 is the first release in which the implementation, the
requirements and this changelog describe the same system.

[Unreleased]: https://github.com/hh-lang1110/Redgum-Tutoring-Appointment-Management-System/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/hh-lang1110/Redgum-Tutoring-Appointment-Management-System/releases/tag/v1.0.0
