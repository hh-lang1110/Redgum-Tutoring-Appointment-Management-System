## What this changes

<!-- One or two sentences. What was wrong or missing before? -->

## Why

<!-- The reasoning. If it fixes a defect, say what the user-visible
     symptom was and what the cause turned out to be. -->

## How it was verified

<!-- The commands you ran and what they showed. "Tests pass" is weaker
     than the specific behaviour you checked. -->

- [ ] `ruff check .` passes
- [ ] `pytest` passes
- [ ] If models changed: `flask db migrate` was run and the generated
      revision was read before committing
- [ ] `CHANGELOG.md` updated, if the change is user-visible

## Checklist

- [ ] One concern only; unrelated tidy-ups are in their own branch
- [ ] New behaviour is covered by a test, or the reason it cannot be is
      explained above
- [ ] No secrets, `.env` files, `instance/` contents or `*.sqlite3` files
      are included
- [ ] Validation limits still match the column widths in `app/models.py`
