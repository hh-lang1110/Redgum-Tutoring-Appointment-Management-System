# Redgum Tutoring Appointment Management System — System Function Design

**Author:** Vivian (Business & Requirements Lead)
**Reviewed by:** Eva (Project Manager), Charon (Technical Lead)
**Status:** Approved at the requirements review
**Version:** 1.0
**Date:** Day 1
**Covers:** WBS 4.1 – 4.5 (System Function Design)

---

## 0. How this document relates to the other two

Three documents describe this system, and each answers a different question:

| Document | Question it answers |
|---|---|
| `docs/requirements.md` | What must the centre be able to do? |
| `docs/design.md` *(this file)* | How is each module put together? |
| `docs/traceability.md` | Which requirement is met by which code, and which test proves it? |

The requirements specification says *what* the centre needs. This document,
the output of WBS 4.1–4.5, says *how* each of the five modules is built: the
fields it holds, the screens staff use, the rules that must hold when they
save, and the message they see when a rule is broken. Requirement IDs from
`docs/requirements.md` (`TR`/`SR`/`BR`/`TT`/`ST`) are cited throughout, so
every design decision can be checked back against the requirement it serves.

Two conventions are used below. **Must** marks a rule that is enforced in
code and refuses the save. Every module is described in the same four
parts: data, screens, rules, errors.

## 1. Module map

| Module | WBS | Requirements | Implemented in | URL prefix |
|---|---|---|---|---|
| Tutor profiles & availability | 4.1 | TR-1 – TR-5 | `app/routes/tutors.py` | `/tutors` |
| Student profiles | 4.2 | SR-1 – SR-5 | `app/routes/students.py` | `/students` |
| Lesson booking | 4.3 | BR-1 – BR-5 | `app/routes/sessions.py` | `/sessions` |
| Timetable | 4.4 | TT-1 – TT-3 | `app/routes/schedule.py` | `/schedule` |
| Statistics | 4.5 | ST-1 – ST-4 | `app/routes/stats.py` | `/stats` |

Every module offers the same four screens: a **list**, a **form**, a
**view**, and the read-only screen that makes the module useful. Staff learn
the pattern once and it holds everywhere.

The booking rule shapes the whole design: a lesson is a slot of time claimed
by a tutor *and* by a room, and neither may be claimed twice. The booking
module (§4) enforces it; the timetable (§5) shows the result; the
dashboard (§6) counts it. The tutor module (§2) supplies the
availability windows the rule is measured against.

## 2. Tutor profile module (WBS 4.1)

**Purpose.** Hold the tutors the centre employs, the subjects each is
qualified to teach, and when each is available to teach them.

### 2.1 Data held

| Field | Type / width | Required | Notes |
|---|---|---|---|
| `name` | text, 120 | yes | TR-5 |
| `subjects` | text, 255 | yes | comma-separated; at least one |
| `qualification` | text, 120 | no | free text |
| `phone` | text, 40 | no | |
| `email` | text, 120 | no | |
| `is_active` | boolean | yes | defaults to active |
| `created_at` | datetime | yes | UTC |

Availability is its own record, not two columns on the tutor, because
a tutor may be available on several days, and more than once on a single
day.

| Field | Type | Notes |
|---|---|---|
| `day_of_week` | integer | 0 = Monday … 6 = Sunday |
| `start_time`, `end_time` | text, 5 | `HH:MM`, 24-hour |

### 2.2 Screens

- **List** (`/tutors/`) — active tutors first, then alphabetical (TR-1).
- **New / edit** (`/tutors/new`, `/tutors/<id>`) — one form for both
  operations (TR-2, TR-3). Writing it once means a field added later cannot
  drift apart between creating and editing.
- **Deactivate / reactivate** — buttons on the edit form, not a
  separate delete screen (TR-4).
- **Availability windows** — added and removed from the edit screen, so a
  tutor's details and their availability are set up in one place.

### 2.3 Rules

1. **Name and subjects are required** (TR-5). Contact details are optional:
   the centre does not always hold an email when a tutor starts, and
   blocking the record on it would push staff back onto paper. Every text
   field is still length-checked against its column width.
2. **Deactivating a tutor is a soft delete** (TR-4). The record stays, with
   its history. A tutor is never removed from the database, because past
   lessons point at them.
3. **An availability window must be a real range**: `end` strictly after
   `start`, both in `HH:MM` form. A window stored as `25:00`, or one that
   ends before it starts, can never be satisfied, which would make the tutor
   unbookable with no error raised anywhere.
4. **Two windows for the same tutor on the same weekday must not overlap.**
   Adjacent windows (`09:00–12:00` then `12:00–14:00`) *are* allowed: they
   mean a continuous morning, and refusing them would force staff to record
   one long window instead.
5. **Availability may only be recorded for Monday to Saturday.** The day
   picker offers exactly the days the timetable can display (TT-1); a window
   on a day nothing can be booked into would be invisible.
6. **A partial form submission never clears a stored value.** If a field is
   absent from the POST, the record keeps what it already had, so a form
   submitted without every control cannot wipe a tutor's contact details.

### 2.4 Errors

| Situation | Message shown |
|---|---|
| no name, or no subjects | "Name and subjects are required." |
| a field longer than its column | "\<Label\> must be *N* characters or fewer." |
| reversed window | "The window must end after it starts." |
| malformed time | "Times must be in 24-hour HH:MM form." |
| overlapping window | "This overlaps the existing window HH:MM–HH:MM." |
| a weekday the grid cannot show | "Choose a weekday for the availability window." |

## 3. Student profile module (WBS 4.2)

**Purpose.** Hold the students the centre teaches and the subjects each is
enrolled in.

### 3.1 Data held

| Field | Type / width | Required | Notes |
|---|---|---|---|
| `name` | text, 120 | yes | SR-5 |
| `year_level` | text, 20 | no | free text; the centre's own wording, not a fixed grade list |
| `parent_name` | text, 120 | no | |
| `parent_phone` | text, 40 | no | |
| `parent_email` | text, 120 | no | |
| `enrolled_subjects` | text, 255 | no | comma-separated |
| `is_active` | boolean | yes | |
| `created_at` | datetime | yes | |

`year_level` is free text, not a fixed set of values. The centre enrols
students across year levels and refers to them in its own words; a list
invented at design time would be wrong by the second term.

### 3.2 Screens

- **List** (`/students/`) — active students first, then alphabetical (SR-1).
- **New / edit** (`/students/new`, `/students/<id>`) (SR-2, SR-3).
- **Deactivate / reactivate** on the edit form (SR-4).
- **Session history** (`/students/<id>/sessions`) — every lesson the student
  has had, newest first. This is the screen the centre uses when a parent
  telephones to ask about attendance.

### 3.3 Rules

1. **Name is required** (SR-5); every other field is optional.
2. **Soft delete**, exactly as for tutors (SR-4). A student's lesson history
   has to survive the student being made inactive, or the attendance record
   the parent asked about would vanish with them.
3. **Length-checked** against every column width, as in §2.3.

### 3.4 Errors

The same shape as §2.4, with "Student" substituted where the form differs.

## 4. Lesson booking module (WBS 4.3)

**Purpose.** The core transaction of the system: one student, one tutor,
one subject, one date, one start time, one duration, one room.

### 4.1 Data held

| Field | Type / width | Notes |
|---|---|---|
| `tutor_id` | foreign key → tutors | |
| `student_id` | foreign key → students | |
| `subject` | text, 80 | must be taught *and* enrolled (BR-4) |
| `session_date` | date | a real date, not a weekday |
| `start_time` | text, 5 | `HH:MM` |
| `duration_minutes` | integer | default 60; between 30 and 480 |
| `room` | text, 40 | free text; may be blank |
| `status` | text, 20 | booked / attended / cancelled / missed |
| `notes` | text, 255 | |
| `created_at` | datetime | |

### 4.2 Screens

- **List** (`/sessions/`), with an optional `?date=` filter (BR-5).
- **Book** (`/sessions/new`) (BR-1).
- **Move** (`/sessions/<id>/move`) — change the date, time, duration or
  room of a lesson that already exists.
- **Status** (`/sessions/<id>/status`) — mark a lesson attended, cancelled
  or missed (BR-5).
- **A tutor's own view** (`/sessions/tutor/<id>`) — that tutor's upcoming
  booked lessons, which is how a tutor checks their day.

### 4.3 Rules

| # | Rule | Enforced in |
|---|---|---|
| BR-1 | The lesson must fall entirely inside one of the tutor's availability windows for that weekday. | `Tutor.can_fit` |
| BR-2 | The tutor must not be double-booked. | `Session.find_clash` → `tutor` |
| BR-3 | The room must not be double-booked. | `Session.find_clash` → `room` |
| BR-4 | The subject must be one the tutor teaches **and** one the student is enrolled in. | `Tutor.teaches`, `Student.enrolled_in` |
| BR-5 | Lessons can be listed, moved and cancelled; cancelling changes the status instead of deleting the row. | `sessions.py` |

Five further rules follow from those:

6. **Duration is bounded** to 30–480 minutes. A zero or negative duration is
   not a cosmetic problem. Every rule above compares a start against an end,
   and a lesson that ends before it begins passes `can_fit`, because its end
   sits inside the window, and reports no clash, because the comparison that
   would find one is false by construction. It could then be booked straight
   on top of an existing lesson with the conflict check never firing.
7. **Monday to Saturday only.** A Sunday lesson would be accepted, stored
   and counted by the dashboard, but could not be rendered in the timetable,
   so staff could book a lesson they had no way to see (TT-1).
8. **Cancelled lessons occupy nothing.** A cancelled lesson blocks neither
   the tutor nor the room, and does not appear in the timetable.
9. **Back-to-back lessons are allowed.** `09:00–10:00` and `10:00–11:00`
   with the same tutor do not overlap; only genuine intersection is
   refused.
10. **A lesson being moved does not clash with itself**: the check excludes
    the row being edited.

### 4.4 Errors

- "All fields are required."
- "*Tutor* is not listed to teach *subject*."
- "*Student* is not enrolled in *subject*."
- "*Tutor* has no availability recorded for *Weekday*."
- "*Tutor* is only available *Weekday* HH:MM–HH:MM; the requested session
  does not fit inside any window."
- "*Tutor or room* is already booked HH:MM–HH:MM on YYYY-MM-DD."
- "Duration must be at least 30 minutes." / "…no more than 480 minutes."
- "Sessions can only be booked Monday to Saturday."

## 5. Timetable module (WBS 4.4)

**Purpose.** The weekly grid, the screen that replaces the paper diary.

### 5.1 Layout

- One week at a time, **Monday to Saturday** (TT-1).
- Days run down the page; each day lists its lessons in start-time order.
- Day names come from the same list the rest of the system uses, so
  "Saturday" cannot mean two different things in two places.

### 5.2 Filters (TT-2)

Three optional filters, read from the querystring: `tutor`, `student`,
`room`. They combine: a tutor *and* a room narrows to that tutor's lessons
in that room.

- **Room matching is case-insensitive**, because room labels are free text
  and "room 2" and "Room 2" are the same room.
- **The active filters are carried into the previous- and next-week links**,
  so paging through the term does not drop the filter and leave staff
  reading the wrong week.
- **Filter lists offer active records only**: a deactivated tutor is not
  offered as a filter.

### 5.3 Cell contents (TT-3)

Each cell shows the booked subject and the counterpart party: the tutor when
the reader is thinking about a student, the student when thinking about a
tutor. Cancelled lessons are not displayed.

### 5.4 Week navigation

`?week=YYYY-MM-DD`, where any date inside the target week selects that week
(the view snaps to its Monday). A value that cannot be parsed falls back to
the current week instead of erroring. A mistyped link should show the
timetable, not a stack trace.

### 5.5 Displayed hours

The hours the grid draws come from `TIMETABLE_START_HOUR` and
`TIMETABLE_END_HOUR` (default 09:00–20:00). These are configuration, not
constants: a centre that opens at eight does not need a code change.

## 6. Statistics module (WBS 4.5)

**Purpose.** The four operational numbers the centre asked for (ST-1 – ST-4).

| # | Number | Definition |
|---|---|---|
| ST-1 | Active tutors | tutors with `is_active = true` |
| ST-2 | Active students | students with `is_active = true` |
| ST-3 | Lessons booked this week | non-cancelled lessons dated inside the displayed week |
| ST-4 | Subject distribution | those lessons counted per subject, most-booked first |

A few notes on these:

- **The statistic week runs Monday to Sunday, while the timetable shows
  Monday to Saturday.** The difference is intentional. The timetable is a
  working view of when rooms are occupied; the statistic
  is a count of what was booked. A Saturday-evening lesson still belongs to
  the week that contains it, so the two screens legitimately disagree about
  the boundary.
- **Cancelled lessons are excluded** from ST-3 and ST-4, so the number
  reflects lessons that will actually run, not lessons that once existed.
- **An empty week renders zeroes and an empty bar list**, not a
  division-by-zero error. A centre with no bookings is a normal state.
- **The dashboard navigates by week with the same `?week=` parameter as the
  timetable**, so moving between the two screens behaves identically.

## 7. Cross-module concerns

### 7.1 The validation layer

Length and time-string checks live in `app/validation.py` and are called by
the route modules before anything is written to the database.

It exists because development runs on SQLite and production on PostgreSQL.
SQLite will silently store a 5,000-character name in a `VARCHAR(120)`
column; PostgreSQL raises. Without the check, a value that saves cleanly on
a developer's machine returns a 500 in production. Validating up front makes
the two environments behave the same, and turns a crash into a readable
form message.

### 7.2 Soft delete

Tutors and students are deactivated, never deleted; lessons are cancelled,
never deleted. Every record a lesson points at must survive, or the history
it is part of breaks.

### 7.3 Inactive records

Inactive tutors and students disappear from booking and filter dropdowns,
but their past lessons still render in lists, in a student's history and in
the statistics. Deactivating a tutor retires them from future booking
without rewriting the past.

### 7.4 Error pages

Missing records and unexpected errors get their own pages, not a default
traceback. A redirect target supplied by an external site is not
followed.

## 8. Design decisions and the alternatives rejected

| Decision | Alternative rejected | Reason |
|---|---|---|
| `Session` entity | `Booking` | "Booking" also names the *act*; naming the record after what it produces keeps the routes unambiguous. |
| `session_date` (real date) | `weekday` (0–5) | A weekday cannot say *which* week, so the timetable could not be paged forward or back. |
| `status` (four values) | `is_cancelled` (boolean) | A boolean cannot record that a lesson was attended or missed, and the centre records both today. |
| `TutorAvailability` entity | start/end columns on the tutor | A tutor is available on several days, sometimes twice in a day. |
| Availability checked against existing windows | accept any window | Overlapping windows make "is this tutor free?" ambiguous, which is the one question the grid must answer. |
| Room as free text | a `rooms` table | The centre keeps a handful of rooms and renames them; a table is overhead. Matching is case-insensitive instead. |
| Duration bounded 30–480 min | accept any integer | A non-positive duration defeats every clash check (§4.3, rule 6). |

---

— End of System Function Design —
