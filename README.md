# Maktab LMS backend

This repository contains the backend-only Django project. The current stage is P003. The custom user model and its initial migration are in place; the project database is not migrated until P004.

## Local setup

Python 3.12 is used through the project virtual environment. Create `.env` from `.env.example` only if you do not already have a local `.env`; do not overwrite an existing environment file.

```sh
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.lock
cp -n .env.example .env
set -a
. ./.env
set +a
.venv/bin/python manage.py check
.venv/bin/python manage.py runserver
```

For an already configured virtual environment, skip the `venv` creation command. The lock was generated with `pip freeze` from the Python 3.12 project environment; refresh it after intentionally changing the direct dependencies:

```sh
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m pip freeze > requirements.lock
```

`requirements.txt` pins direct dependencies. `requirements.lock` pins the resolved direct and transitive package versions used for repeatable installation. Secrets belong in the ignored local `.env` or the deployment environment, never in source control.

`DEBUG=1` is for local development. Shared or production environments must set `DEBUG=0`, provide a private `SECRET_KEY`, and set the correct `ALLOWED_HOSTS`. Production deployment hardening is handled in later prompts.

The `accounts.User` model uses Django's standard `create_user()` / `set_password()` path; passwords are stored as hashes. The first real database migration is reserved for P004 after PostgreSQL is configured.
