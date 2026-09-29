"""Smoke test: boot the app, seed data, hit every route."""
import traceback
from app import create_app
from app.models import db


def main():
    app = create_app("testing")
    with app.app_context():
        db.create_all()
        from app.seed import seed_database
        seed_database()
        client = app.test_client()
        for url in ["/", "/stats/", "/tutors/", "/students/", "/bookings/", "/timetable/"]:
            try:
                resp = client.get(url)
                print(f"  {url} -> {resp.status_code}")
                assert resp.status_code in (200, 302), (url, resp.status_code)
            except Exception:
                print(f"FAILED on {url}:")
                traceback.print_exc()
                raise
        print("All routes OK.")


if __name__ == "__main__":
    main()
