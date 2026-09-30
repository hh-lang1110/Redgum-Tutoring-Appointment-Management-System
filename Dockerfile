FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_ENV=production

WORKDIR /app

# Requirements first so the dependency layer is cached across code changes.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Run as a non-root user. Creating it after the copy keeps the build cache
# useful, and giving it ownership means the app can write its instance folder.
RUN useradd --create-home --shell /usr/sbin/nologin redgum \
    && chown -R redgum:redgum /app
USER redgum

EXPOSE 5000

# The app refuses to start in production without a real SECRET_KEY, so a
# misconfigured container fails immediately rather than serving with a
# known-public key.
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:5000/')"

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "run:app"]
