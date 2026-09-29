# Redgum Tutoring Appointment Management System — Requirements Specification

**Author:** Vivian (Business & Requirements Lead)
**Status:** Approved by PM (Eva)
**Version:** 1.0
**Date:** Day 1

---

## 1. Business Background

Redgum Tutoring is a single-centre private tutoring institution. Today, tutor profiles, student profiles and lesson bookings are maintained on paper registers and shared spreadsheets. This causes:

- Lost or damaged paper records during handovers.
- Slow, error-prone record lookups (several minutes per query).
- Double-booking of a tutor or a room at the same time slot.
- Slow weekly timetable reconfiguration.
- No quick way to produce operational statistics.

The system is a **lightweight internal web application** used by centre staff only. It is **not** a customer-facing portal.

## 2. Functional Requirements

### 2.1 Tutor Profile Management
| ID | Requirement |
|---|---|
| TR-1 | List all tutors with name, subjects, qualification, contact and availability. |
| TR-2 | Create a new tutor record. |
| TR-3 | View and edit an existing tutor record. |
| TR-4 | Mark a tutor as inactive (soft delete) instead of removing history. |
| TR-5 | Validate required fields: name, at least one subject, contact email/phone. |

### 2.2 Student Profile Management
| ID | Requirement |
|---|---|
| SR-1 | List all students with name, grade level, parent contact and enrolled subjects. |
| SR-2 | Create a new student record. |
| SR-3 | View and edit an existing student record. |
| SR-4 | Mark a student as inactive (soft delete). |
| SR-5 | Validate required fields: name, grade, parent contact. |

### 2.3 Lesson Booking
| ID | Requirement |
|---|---|
| BR-1 | Book a lesson: choose tutor, student, subject, weekday, start time, duration and room. |
| BR-2 | Prevent **tutor double-booking**: the same tutor cannot have two lessons overlapping in time. |
| BR-3 | Prevent **room double-booking**: the same room cannot host two lessons overlapping in time. |
| BR-4 | The booked subject must be one of the tutor's subjects and one of the student's enrolled subjects. |
| BR-5 | List, view and cancel bookings. Cancellation soft-deletes the booking. |

### 2.4 Timetable View
| ID | Requirement |
|---|---|
| TT-1 | Weekly timetable grid (Monday–Saturday, 09:00–20:00). |
| TT-2 | Filter the grid by tutor, by student or by room. |
| TT-3 | Each cell shows the booked subject and the counterpart party. |

### 2.5 Statistics Dashboard
| ID | Requirement |
|---|---|
| ST-1 | Number of active tutors. |
| ST-2 | Number of active students. |
| ST-3 | Number of lessons booked in the current week. |
| ST-4 | Subject distribution of bookings (simple bar list). |

## 3. Non-Functional Requirements

- **NFR-1 — Usability:** Internal staff only; no public sign-up. Single role "Staff".
- **NFR-2 — Performance:** Page load under 2 s on a local development machine; < 500 records.
- **NFR-3 — Portability:** Runs on Python 3.11+; SQLite by default, PostgreSQL compatible via environment variable.
- **NFR-4 — Configuration:** No secrets in source code; all environment-specific values read from `.env`.
- **NFR-5 — Deployability:** Provides a `Dockerfile` and a `Procfile` for a PaaS such as Render.

## 4. Out of Scope (Explicitly)

- Online payment, invoicing, payroll.
- Student self-service portal or parent mobile app.
- Automated SMS / email notifications, marketing.
- Multi-branch, multi-lingual support.
- Detailed financial accounting.

## 5. Data Model (Logical)

- **Tutor**: id, name, subjects (CSV), qualification, phone, email, availability_note, is_active, created_at.
- **Student**: id, name, grade_level, parent_name, parent_phone, parent_email, enrolled_subjects (CSV), is_active, created_at.
- **Booking**: id, tutor_id (FK), student_id (FK), subject, weekday (0=Mon … 5=Sat), start_time, duration_minutes, room, is_cancelled, created_at.

## 6. Acceptance Criteria

1. All five modules (tutors, students, bookings, timetable, stats) are reachable from the navigation.
2. Creating two overlapping bookings for the same tutor or same room is rejected with a clear error message.
3. The weekly timetable renders bookings correctly for at least one filter dimension.
4. The dashboard numbers match the underlying database counts.
5. The application starts with `flask run` after copying `.env.example` to `.env`.
