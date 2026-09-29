web: gunicorn --bind 0.0.0.0:$PORT run:app
release: flask --app run.py seed-db || true
