"""Entry point for local development.

Author: Charon (Technical Lead)
"""
import os

from app import create_app

app = create_app()

if __name__ == "__main__":
    # The interactive debugger is opt-in via FLASK_DEBUG and the bind address
    # defaults to loopback, so a plain ``python run.py`` can no longer expose
    # the debugger (or the app itself) to the local network by accident.
    app.run(
        host=os.environ.get("FLASK_RUN_HOST", "127.0.0.1"),
        port=int(os.environ.get("FLASK_RUN_PORT", "5000")),
        debug=os.environ.get("FLASK_DEBUG", "").strip().lower() in {"1", "true", "yes"},
    )
