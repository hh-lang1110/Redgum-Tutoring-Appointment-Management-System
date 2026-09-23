import os
import sqlite3
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent

db_setting = Path(os.environ.get("DB_PATH", "data/redgum.sqlite3"))
DB_PATH = db_setting if db_setting.is_absolute() else ROOT / db_setting

HOST = os.environ.get("HOST", "127.0.0.1")
PORT = int(os.environ.get("PORT", "8000"))


def initialize_database():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH)
    connection.close()


class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            status = 200
            message = "OK\n"
        elif self.path == "/":
            status = 200
            message = "Redgum Tutoring Appointment Management System\n"
        else:
            status = 404
            message = "Not found\n"

        body = message.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def main():
    initialize_database()

    with ThreadingHTTPServer((HOST, PORT), RequestHandler) as server:
        print(f"Server running at http://{HOST}:{PORT}")
        print(f"SQLite database: {DB_PATH}")
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")


if __name__ == "__main__":
    main()
