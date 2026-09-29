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
