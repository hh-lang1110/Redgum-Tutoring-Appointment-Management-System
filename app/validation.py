"""Request-payload validation shared by the route modules.

Two classes of problem are worth catching here rather than at the database.

**Length.** SQLite silently stores a 5,000-character name in a VARCHAR(120)
column; PostgreSQL raises. Development runs on SQLite and production on
PostgreSQL, so without this check a name that saves fine locally returns a
500 in production. Validating up front keeps the two environments behaving
the same and turns the failure into a readable form message.

**Time strings.** The booking rules are expressed in terms of availability
windows, so a window stored as "25:00" or one that ends before it starts is
not merely untidy: it can never be satisfied, which would silently make a
tutor unbookable with no error anywhere.
"""
from .models import to_minutes

# The weekly grid renders Monday to Saturday, so Saturday is the last
# bookable weekday (TT-1).
LAST_BOOKABLE_WEEKDAY = 5

MIN_DURATION_MINUTES = 30
MAX_DURATION_MINUTES = 480

# Field name -> maximum length, mirroring the column widths in models.py.
MAX_LENGTH = {
    "name": 120,
    "subjects": 255,
    "qualification": 120,
    "phone": 40,
    "email": 120,
    "year_level": 20,
    "parent_name": 120,
    "parent_phone": 40,
    "parent_email": 120,
    "enrolled_subjects": 255,
    "subject": 80,
    "room": 40,
    "notes": 255,
}

# Field name -> the wording used in the form, so messages read naturally
# ("Student name" rather than "Name" on the student form).
LABELS = {
    "name": "Name",
    "subjects": "Subjects",
    "qualification": "Qualification",
    "phone": "Phone",
    "email": "Email",
    "year_level": "Year level",
    "parent_name": "Parent name",
    "parent_phone": "Parent phone",
    "parent_email": "Parent email",
    "enrolled_subjects": "Enrolled subjects",
    "subject": "Subject",
    "room": "Room",
    "notes": "Notes",
}


def length_errors(values):
    """Return a message for every field in ``values`` that is too long.

    ``values`` maps a field name from :data:`MAX_LENGTH` to the submitted
    string; unknown fields are ignored so callers can pass a whole form
    without filtering it first.
    """
    errors = []
    for field, value in values.items():
        limit = MAX_LENGTH.get(field)
        if limit and value and len(value) > limit:
            label = LABELS.get(field, field.replace("_", " ").capitalize())
            errors.append(f"{label} must be {limit} characters or fewer.")
    return errors


def duration_error(minutes):
    """Validate a session length, or return ``None`` when it is usable.

    A non-positive duration is the dangerous case rather than a cosmetic one.
    Every time-based rule here compares a start against an end, so a session
    with a negative length ends before it begins. It then passes
    ``can_fit`` - the "end" falls inside the availability window - and
    ``overlaps`` reports no collision with anything, because the comparison
    that would find one is false by construction. The result is a session
    that can be booked directly on top of an existing lesson without the
    conflict check firing, and that renders as an end time earlier than its
    start.
    """
    if minutes is None:
        return "Duration is required."
    if minutes < MIN_DURATION_MINUTES:
        return f"Duration must be at least {MIN_DURATION_MINUTES} minutes."
    if minutes > MAX_DURATION_MINUTES:
        return f"Duration must be no more than {MAX_DURATION_MINUTES} minutes."
    return None


def timetable_day_error(day):
    """Reject a date the weekly timetable cannot display.

    The grid covers Monday to Saturday (TT-1). A session on a Sunday is
    accepted, stored and counted by the statistics dashboard, but appears
    nowhere in the timetable, so staff would have no way to see a lesson
    they had booked.
    """
    if day is None:
        return "A valid date is required."
    if day > LAST_BOOKABLE_WEEKDAY:
        return "Sessions can only be booked Monday to Saturday."
    return None


def window_error(start, end, existing=()):
    """Validate one availability window against the tutor's existing ones.

    ``existing`` is the tutor's windows for the same weekday, so that two
    overlapping windows cannot both be stored. Returns ``None`` when the
    window is usable, otherwise a message explaining why it is not.
    """
    start_min, end_min = to_minutes(start), to_minutes(end)
    if start_min is None or end_min is None:
        return "Times must be in 24-hour HH:MM form."
    if start_min >= end_min:
        return "The window must end after it starts."
    for window in existing:
        other_start = to_minutes(window.start_time)
        other_end = to_minutes(window.end_time)
        if other_start is None or other_end is None:
            continue
        if start_min < other_end and other_start < end_min:
            return (f"This overlaps the existing window "
                    f"{window.start_time}-{window.end_time}.")
    return None
