# Committed on purpose: these are non-secret defaults that let `flask` and
# `flask db` find the application without any per-developer setup.
# Local overrides belong in .env, which is git-ignored.
FLASK_APP=run.py
FLASK_ENV=development
