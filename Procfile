web: gunicorn --bind 0.0.0.0:$PORT run:app
# Apply migrations on release. This deliberately does NOT run `flask seed-db`:
# that command loads the demo tutors and students from seed.py, which must
# never reach a real database. Letting a failed migration pass with `|| true`
# would also start the new code against an old schema, so failures stop the
# deploy instead.
release: flask db upgrade
