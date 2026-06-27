# Contributing Guide

This project follows a clean ETL development workflow focused on maintainable Python code, safe SQL operations, and consistent Git/GitHub collaboration.

## Branch Strategy

- `main`: stable production-ready branch
- `feature/<short-name>`: feature development branch
- `fix/<short-name>`: bug fix branch
- `docs/<short-name>`: documentation updates

## Standard Workflow

1. Pull latest changes from `main`.
2. Create a branch from `main`.
3. Make focused commits with clear messages.
4. Run local checks before pushing:
   - `python -m compileall .`
   - `python pipeline.py`
5. Push branch to GitHub and open a Pull Request.
6. After review, merge to `main`.

## Commit Message Format

Use concise, descriptive messages:

- `feat: add ETL engine orchestration class`
- `fix: handle invalid DB env configuration`
- `docs: add CockroachDB connection setup`

## Code Quality Expectations

- Use Object-Oriented Programming principles (single responsibility, reusable classes, composition).
- Keep methods small and named by intent.
- Raise explicit errors for invalid configuration states.
- Keep database writes transaction-safe and conflict-aware.
- Add documentation updates alongside behavior changes.

## SQL and Storage Safety

- Never interpolate SQL values with string formatting.
- Use parameterized SQL statements.
- Roll back transactions on failures.
- Use idempotent load strategy (`skip`) or upsert strategy (`upsert`) based on `LOAD_MODE`.

## Documentation Requirements

Every meaningful pipeline change should update:

- `README.md` for setup/run behavior
- This contributing guide for workflow policy (if needed)
- Inline code comments only where logic is non-obvious
