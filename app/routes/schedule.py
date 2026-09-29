"""Week schedule view (Mon-Sat). No room allocation per case-study scope."""
from datetime import date, timedelta
from flask import Blueprint, render_template, request
from ..models import Session, WEEKDAY_NAMES

bp = Blueprint("schedule", __name__, url_prefix="/schedule")


def _monday(d):
    return d - timedelta(days=d.weekday())


@bp.route("/")
def weekly():
    week_param = request.args.get("week", "")
    try:
        base = date.fromisoformat(week_param)
    except Exception:
        base = date.today()
    monday = _monday(base)
    days = [monday + timedelta(days=i) for i in range(6)]  # Mon..Sat
    rows = []
    for d in days:
        sessions = (Session.query
                    .filter(Session.session_date == d,
                            Session.status != "cancelled")
                    .order_by(Session.start_time).all())
        rows.append((d, WEEKDAY_NAMES[d.weekday()], sessions))
    prev_week = (monday - timedelta(days=7)).isoformat()
    next_week = (monday + timedelta(days=7)).isoformat()
    return render_template("schedule/weekly.html", rows=rows,
                           monday=monday, prev_week=prev_week, next_week=next_week)

