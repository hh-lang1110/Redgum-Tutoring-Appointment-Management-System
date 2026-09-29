"""Smoke test: boot the app, seed data, hit every route.

Used by both local manual testing and GitHub Actions CI.
"""
from app import create_app
from app.models import db


def main() -> None:
    app = create_app("testing")
    with app.app_context():
        db.create_all()
        from app.seed import seed_database

        seed_database()
        client = app.test_client()
        urls = ["/", "/stats/", "/tutors/", "/students/", "/bookings/", "/timetable/"]
        for url in urls:
            resp = client.get(url)
            assert resp.status_code in (200, 302), (url, resp.status_code)
            print(f"  {url} -> {resp.status_code}")
        print("All routes OK.")


if __name__ == "__main__":
    main()
