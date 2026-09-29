"""Smoke test: app boots, routes register, availability rule works."""
from app import create_app
from app.models import db, Tutor


def main():
    app = create_app("testing")
    with app.app_context():
        db.create_all()
        rules = sorted(r.rule for r in app.url_map.iter_rules())
        assert "/tutors/" in rules and "/sessions/" in rules, rules
        # Instantiate a tutor and check the availability helper
        t = Tutor(name="Test", subjects="Math")
        db.session.add(t); db.session.commit()
        from app.models import TutorAvailability
        db.session.add(TutorAvailability(tutor_id=t.id, day_of_week=1,
                                         start_time="15:30", end_time="19:00"))
        db.session.commit()
        ok, _ = t.can_fit(1, "16:00", 60)
        assert ok, "inside window should fit"
        ok, _ = t.can_fit(1, "14:00", 60)
        assert not ok, "before window should be rejected"
        print("Smoke test passed: routes registered, availability rule enforced.")


if __name__ == "__main__":
    main()
