# Changelog

All notable changes to this project are documented here.
Format based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added
- Configuration management hardening (pending review).

## [1.0.0] — 2026-09-29

### Added
- Requirements specification (`docs/requirements.md`) covering five functional modules (tutors, students, bookings, timetable, statistics) and non-functional requirements.
- SQLAlchemy data models: `Tutor`, `Student`, `Booking` with soft-delete flags.
- Seed data for local development (3 tutors, 3 students, 4 bookings).
- Flask application factory with environment-driven configuration (`development`, `testing`, `production`).
- Tutor profile CRUD (list, create, edit, activate/deactivate).
- Student profile CRUD (list, create, edit, activate/deactivate).
- Lesson booking with automatic tutor and room conflict detection, subject-matching validation, and soft-cancel.
- Weekly timetable grid (Mon–Sat, 09:00–20:00) filterable by tutor, student or room.
- Statistics dashboard (active tutors, active students, weekly bookings, subject distribution).
- Deployment artefacts: `Dockerfile`, `Procfile` for Render, pinned `requirements.txt`.
- GitHub Actions CI workflow (lint + smoke-test on every push/PR).
- `.env.example` documenting all environment variables.

[Unreleased]: https://github.com/hh-lang1110/Redgum-Tutoring-Appointment-Management-System/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/hh-lang1110/Redgum-Tutoring-Appointment-Management-System/releases/tag/v1.0.0
