# Contributing

## Getting set up

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env          # Windows: copy .env.example .env
flask db upgrade
flask seed-db                 # optional demo data
python run.py
```

## Before opening a pull request

```bash
ruff check .
pytest
```

Both must pass; CI runs the same two commands on Python 3.11 and 3.12.

## Branches

Branch from `main` and merge back with `--no-ff`, so the history keeps a
record of the change as a unit:

| Prefix | Use |
|---|---|
| `feature/` | new behaviour |
| `fix/` | corrected behaviour |
| `build/` | tooling, dependencies, deployment |
| `docs/` | documentation only |
| `chore/` | housekeeping with no behaviour change |

Keep a branch to one concern. A branch that fixes a bug and reformats a
module is two branches.

## Commit messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):
`type: summary in the imperative mood`, using the same type prefixes as
above. The body should say what was wrong or missing and why the change is
the right fix; a reader six months from now cares about the reasoning far
more than the diff, which they can already see.

```
fix: reject availability windows that end before they start

A window stored as 19:00-15:00 can never be satisfied, so the tutor
silently becomes unbookable with no error anywhere.
```

## Migrations

The schema is owned by Alembic. Never reintroduce `db.create_all()` outside
the test suite: it only adds missing tables and silently ignores new columns
on a table that already exists.

```bash
flask db migrate -m "add X to Y"
```

**Always read the generated migration before committing it.** Alembic does
not detect column renames and will emit a drop plus an add, which loses the
data in that column. Batch mode is enabled (`render_as_batch`) so SQLite can
perform the table rebuild that `ALTER` and `DROP` require.

CI fails if the models and the migrations disagree.

## Tests

Add tests with behaviour, not with files. Where a rule lives in the model,
test it in `tests/test_models.py`; where a route enforces it, add an
endpoint test as well, because the rule is only worth anything if a request
that breaks it is actually refused.

Fixtures for the common cases (`make_tutor`, `make_student`, `seeded`) are in
`tests/conftest.py`.

## Handling data

- Never commit `.env`, `instance/`, or any `*.sqlite3` file; `.gitignore`
  covers these.
- Validation limits in `app/validation.py` mirror the column widths in
  `app/models.py`. If a column width changes, change both.
