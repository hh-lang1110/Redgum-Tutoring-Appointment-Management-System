# Requirement Traceability Matrix

**Author:** Vivian (Business & Requirements Lead)
**Reviewed by:** Eva (Project Manager), Charon (Technical Lead)
**Status:** Approved at the requirements review (WBS 2.7)
**Version:** 1.0
**Date:** Day 1

---

Every requirement in `docs/requirements.md` is listed here once, against the
code that meets it and the automated test that proves it.

Where a requirement has no direct test, that is said so in §9, instead of
being matched to a test that covers something close to it.

Test names are given without their `test_` prefix or file, except where the
file matters. The suite collects 111 tests across five files:

| Test file | Tests | Covers |
|---|---|---|
| `tests/test_models.py` | 34 | domain rules on the model layer |
| `tests/test_routes.py` | 25 | each screen, form and error path |
| `tests/test_booking_rules.py` | 24 | the booking rules end to end |
| `tests/test_schedule_filters.py` | 15 | the weekly grid and its filters |
| `tests/test_stats.py` | 13 | the dashboard's numbers |

## 1. Tutor profile management (TR)

| ID | Requirement | Met in | Proved by |
|---|---|---|---|
| TR-1 | List all tutors with name, subjects, qualification, contact and availability. | `routes/tutors.py::list_tutors`, `templates/tutors/list.html` | `all_main_pages_render` |
| TR-2 | Create a new tutor record. | `routes/tutors.py::new_tutor` | `tutor_can_be_created_and_edited` |
| TR-3 | View and edit an existing tutor record. | `routes/tutors.py::edit_tutor` | `tutor_can_be_created_and_edited`, `editing_a_tutor_does_not_wipe_absent_fields` |
| TR-4 | Mark a tutor inactive (soft delete); history is kept. | `routes/tutors.py::edit_tutor` | `deactivate_keeps_the_tutor_record` |
| TR-5 | Validate: name and at least one subject required; contact optional but length-checked. | `validation.py::length_errors`, `new_tutor` | `tutor_without_a_name_is_refused`, `over_long_tutor_name_is_refused_not_truncated` |

Supporting rules from §2.3 of the design, each with its own test:

| Rule | Proved by |
|---|---|
| A window must end after it starts | `reversed_window_is_refused` |
| Times must be `HH:MM` | `malformed_time_is_refused` |
| Same-day windows must not overlap | `overlapping_window_is_refused` |
| Adjacent windows *are* allowed | `adjacent_window_is_allowed` |
| Windows on different days do not collide | `window_on_a_different_day_does_not_overlap` |
| Only Monday–Saturday may be recorded | `sunday_availability_is_refused`, `invalid_weekday_is_refused`, `the_day_dropdown_offers_monday_to_saturday` |
| A window can be removed | `window_can_be_deleted`, `valid_window_is_stored` |

## 2. Student profile management (SR)

| ID | Requirement | Met in | Proved by |
|---|---|---|---|
| SR-1 | List all students with name, year level, parent contact and enrolled subjects. | `routes/students.py::list_students` | `all_main_pages_render` |
| SR-2 | Create a new student record. | `routes/students.py::new_student` | `student_can_be_created` |
| SR-3 | View and edit an existing student record. | `routes/students.py::edit_student` | `student_can_be_created` |
| SR-4 | Mark a student inactive (soft delete). | `routes/students.py::edit_student` | **no direct test, see §9** |
| SR-5 | Validate: name required; year level and parent contact optional but length-checked. | `validation.py::length_errors`, `new_student` | `student_without_a_name_is_refused`, `over_long_student_email_is_refused` |
| n/a | Session history renders | `routes/students.py::student_sessions` | `student_session_history_renders` |

## 3. Lesson booking (BR)

| ID | Requirement | Met in | Proved by |
|---|---|---|---|
| BR-1 | A lesson must fall entirely inside one of the tutor's availability windows for that weekday. | `models.py::Tutor.can_fit` | `booking_inside_availability_is_accepted_at_the_edges`, `booking_outside_availability_is_refused`, `booking_on_a_day_with_no_availability_is_refused`, `session_inside_window_fits`, `session_may_use_the_whole_window`, `session_before_window_is_rejected`, `session_overrunning_window_end_is_rejected`, `tutor_without_availability_cannot_be_booked`, `availability_is_per_weekday` |
| BR-2 | A tutor must not be double-booked. | `models.py::Session.find_clash` | `tutor_cannot_be_double_booked`, `find_clash_reports_a_tutor_conflict`, `move_onto_another_session_is_refused` |
| BR-3 | A room must not be double-booked. | `models.py::Session.find_clash` | `room_cannot_be_double_booked`, `find_clash_reports_a_room_conflict`, `find_clash_ignores_a_blank_room` |
| BR-4 | The subject must be one the tutor teaches *and* the student is enrolled in. | `models.py::Tutor.teaches`, `models.py::Student.enrolled_in` | `subject_the_tutor_does_not_teach_is_refused`, `subject_the_student_is_not_enrolled_in_is_refused`, `teaches_ignores_case_and_padding`, `teaches_rejects_other_subjects`, `teaches_does_not_match_partial_words`, `enrolled_in_matches_student_subjects` |
| BR-5 | List, view and cancel bookings; cancelling keeps the record. | `routes/sessions.py` | `status_can_be_changed`, `unknown_status_is_rejected`, `cancelled_sessions_do_not_block_a_slot` |

Supporting rules from §4.3 of the design:

| Rule | Proved by |
|---|---|
| Back-to-back lessons are allowed | `back_to_back_bookings_are_allowed`, `back_to_back_sessions_do_not_overlap` |
| Cancelled lessons block nothing | `cancelled_sessions_do_not_block_a_slot`, `find_clash_ignores_cancelled_sessions` |
| A lesson being moved ignores itself | `moving_a_session_does_not_clash_with_itself`, `find_clash_can_exclude_the_session_being_moved` |
| Clashes are per weekday, not global | `find_clash_ignores_other_weekdays` |
| Duration: 30–480 minutes | `zero_duration_is_refused`, `negative_duration_is_refused`, `absurd_duration_is_refused`, `negative_duration_is_refused_when_moving` |
| A negative duration cannot evade the clash check | `negative_duration_would_otherwise_evade_the_clash_check` |
| Move works, and is refused when the target is unavailable | `move_to_a_free_slot_succeeds`, `move_outside_availability_is_refused` |
| Session end time, including past midnight | `end_time_adds_the_duration`, `end_time_wraps_past_midnight` |
| Overlap detection | `overlapping_sessions_are_detected` |

## 4. Timetable view (TT)

| ID | Requirement | Met in | Proved by |
|---|---|---|---|
| TT-1 | Weekly grid, Monday–Saturday. | `routes/schedule.py::weekly`, `config.py::TIMETABLE_*_HOUR` | `sunday_booking_is_refused`, `saturday_booking_is_still_allowed`, `moving_a_session_to_sunday_is_refused` |
| TT-2 | Filter the grid by tutor, by student or by room. | `routes/schedule.py::_filter_args` | `filtering_by_tutor_shows_only_that_tutors_sessions`, `filtering_by_student`, `filtering_by_room`, `room_filter_ignores_case`, `filters_combine`, `tutor_filters_partition_the_week`, `malformed_filters_do_not_error` |
| TT-3 | Each cell shows the booked subject and the counterpart party. | `templates/schedule/weekly.html` | `unfiltered_grid_shows_every_session`, `a_filter_matching_nothing_reports_zero` |

Supporting behaviour:

| Rule | Proved by |
|---|---|
| Cancelled lessons are not shown | `cancelled_sessions_are_not_shown` |
| Filters survive week navigation | `filters_are_carried_into_week_navigation` |
| An empty filter result is reported, not hidden | `a_filter_matching_nothing_reports_zero`, `unfiltered_view_has_no_match_summary` |

## 5. Statistics dashboard (ST)

| ID | Requirement | Met in | Proved by |
|---|---|---|---|
| ST-1 | Number of active tutors. | `routes/stats.py::dashboard` | `roster_cards_reflect_active_records` |
| ST-2 | Number of active students. | `routes/stats.py::dashboard` | `roster_cards_reflect_active_records` |
| ST-3 | Number of lessons booked in the current week. | `routes/stats.py::dashboard` | `dashboard_counts_only_the_displayed_week`, `cancelled_sessions_are_excluded_from_the_count` |
| ST-4 | Subject distribution of bookings. | `routes/stats.py::subject_distribution` | `subject_distribution_orders_by_count_descending`, `subject_distribution_breaks_ties_alphabetically`, `subject_distribution_handles_an_empty_week` |

Supporting behaviour:

| Rule | Proved by |
|---|---|
| The week runs Monday to Sunday | `week_bounds_runs_monday_to_sunday`, `week_bounds_from_a_sunday_stays_in_the_same_week` |
| An empty week does not divide by zero | `empty_week_renders_without_dividing_by_zero` |
| A bad `week=` value falls back to this week | `unparseable_week_falls_back_to_the_current_week` |
| Week navigation moves exactly one week | `navigation_links_move_a_week_at_a_time` |
| The seeded data reaches the dashboard | `seeded_data_loads_into_the_dashboard`, `dashboard_renders` |

## 6. Non-functional requirements (NFR)

These are properties of how the system is built, not behaviour a unit test
can assert, so each is listed with the artefact that demonstrates it instead
of a test name.

| ID | Requirement | Demonstrated by |
|---|---|---|
| NFR-1 | Internal staff only; single "Staff" role; no public sign-up. | No auth blueprint exists; no registration route in `app/` |
| NFR-2 | Page load under 2 s locally; under 500 records. | Not measured, see §9 |
| NFR-3 | Python 3.11+; SQLite by default, PostgreSQL via environment variable. | `app/config.py` config classes; `DATABASE_URL` |
| NFR-4 | No secrets in source; environment values from `.env`. | `.env.example`, `.gitignore`, and the production guard in `app/config.py` that refuses to start on a placeholder secret |
| NFR-5 | A `Dockerfile` and a `Procfile` for a PaaS. | `Dockerfile`, `Procfile` in the repository root |

## 7. Acceptance criteria → evidence

The five acceptance criteria in §6 of `docs/requirements.md`, against the
test that demonstrates each:

| # | Criterion | Evidence |
|---|---|---|
| 1 | All five modules reachable from the navigation. | `all_main_pages_render` |
| 2 | Overlapping bookings for a tutor or a room are rejected with a clear message. | `tutor_cannot_be_double_booked`, `room_cannot_be_double_booked` |
| 3 | The weekly timetable renders bookings for at least one filter dimension. | `filtering_by_tutor_shows_only_that_tutors_sessions` |
| 4 | The dashboard numbers match the database counts. | `roster_cards_reflect_active_records`, `dashboard_counts_only_the_displayed_week` |
| 5 | The app starts with `flask run` after copying `.env.example`. | CI smoke test (`.github/workflows/`) |

## 8. What the matrix shows

Every functional requirement (TR, SR, BR, TT, ST: 22 in all) is met in
code. Twenty-one of the twenty-two have at least one test naming them
directly; SR-4 is covered by the same code path as TR-4 and is not tested
on the student form in its own right. The non-functional requirements are
demonstrated by artefacts, not tests, with NFR-2 the one property
nobody has measured.

## 9. Gaps

These three are recorded, not left out.

| Gap | Detail | Suggested fix |
|---|---|---|
| **SR-4 has no direct test** | Deactivating a *tutor* is tested (`deactivate_keeps_the_tutor_record`); deactivating a *student* is not, though it is the same code path and the same soft-delete rule. | Add a student equivalent of the tutor test. |
| **NFR-2 is not measured** | "Under 2 s locally, under 500 records" is an assertion nobody has timed. | Seed 500 records and time a request, or restate the requirement as a design goal with no measurement claimed. |
| **TT-3 is proved indirectly** | That cells show the subject *and* the counterpart party is verified through the grid rendering tests, not by asserting the cell contents themselves. | Assert a cell's text for one filtered week. |

---

— End of Requirement Traceability Matrix —
