# Project Scope and Team Workflow

Status: Day 1 working agreement. Confirm the scope and acceptance criteria against the approved Project Charter before treating them as final.

## Project scope

The Redgum Tutoring Appointment Management System is for managing tutoring-centre operations.

### In scope
- Tutor profiles
- Student profiles
- Lesson booking records
- A timetable with week, tutor, student, and room filters
- Weekly management statistics
- Booking conflict checks for the tutor, student, and room

### Out of scope
- Payments and invoicing
- Student or parent self-service
- Notifications
- Payroll
- Multi-centre management

## Team responsibilities

| Member | Role | Branch | Responsibility |
|---|---|---|---|
| Eva (Liu) | Project manager | `feature/eva-project-integration` | Scope coordination, integration, review tracking, and handover |
| Charon (Han) | Technical lead | `feature/charon-technical` | Python server, SQLite persistence, technical configuration, and deployment |
| Vivian (Ke) | Requirements lead | `feature/vivian-requirements` | Business fields, user workflows, interface requirements, and acceptance criteria |

## Branch and pull request workflow

- `main` is the stable integration branch.
- Do project work on the assigned feature branch; do not commit directly to `main`.
- Open a pull request from the feature branch into `main`.
- Include a clear summary, requirement link, verification status, and review notes in each pull request.
- Ask a teammate to review the change. The author should address review comments before merging.
- Merge after the agreed review is complete. Do not report a local or simulated merge as a GitHub pull request.

### Branch names

- `feature/eva-project-integration`
- `feature/charon-technical`
- `feature/vivian-requirements`

### Commit message examples

- `docs: establish project scope and review flow`
- `feat: add tutor and student profiles`
- `fix: reject overlapping lesson bookings`

## Acceptance checklist for the completed product

- [ ] A tutor profile can be created, viewed, edited, and removed.
- [ ] A student profile can be created, viewed, edited, and removed.
- [ ] A lesson booking records its tutor, student, subject, date, time, duration, and room.
- [ ] The system rejects overlapping bookings for the same tutor, student, or room.
- [ ] The timetable can be filtered by week, tutor, student, and room.
- [ ] The dashboard shows the agreed weekly management statistics.
- [ ] The team has reviewed the finished application against the approved Project Charter.
