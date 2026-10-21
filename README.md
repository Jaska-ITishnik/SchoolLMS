# Maktab LMS backend

This repository contains the backend-only Django project. P004 configured the local PostgreSQL database and applied the custom-user migration. P005 adds a synthetic learning-goal endpoint that is disabled unless explicitly enabled for development.

## Local setup

Python 3.12 is used through the project virtual environment. Create `.env` from `.env.example` only if you do not already have a local `.env`; do not overwrite an existing environment file. PostgreSQL is a host service; no Compose or container setup is used.

Install and start the Ubuntu PostgreSQL service:

```sh
sudo apt update
sudo apt install -y postgresql postgresql-client
sudo systemctl start postgresql
sudo systemctl status postgresql
```

Create the local role and database. In the `psql` session, `\password` prompts for the role password without putting it in shell history. If the role or database already exists, inspect it first and do not drop or recreate it.

```sh
sudo -u postgres psql
CREATE ROLE school_lms LOGIN;
\password school_lms
CREATE DATABASE school_lms OWNER school_lms;
\q
```

Set the connection values in the ignored local `.env` (retain its existing secret key):

If no local `.env` exists yet, create it with `cp -n .env.example .env` first.

```text
DB_ENGINE=django.db.backends.postgresql
DB_NAME=school_lms
DB_USER=school_lms
DB_PASSWORD=<the-password-set-for-school_lms>
DB_HOST=127.0.0.1
DB_PORT=5432
```

Then start Django from the project virtual environment:

```sh
set -a
. ./.env
set +a
.venv/bin/python manage.py check
.venv/bin/python manage.py migrate
.venv/bin/python manage.py runserver
```

For an already configured virtual environment, skip the `venv` creation command. The lock was generated with `pip freeze` from the Python 3.12 project environment; refresh it after intentionally changing the direct dependencies:

```sh
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m pip freeze > requirements.lock
```

`requirements.txt` pins direct dependencies. `requirements.lock` pins the resolved direct and transitive package versions used for repeatable installation. Secrets belong in the ignored local `.env` or the deployment environment, never in source control.

`DEBUG=1` is for local development. Shared or production environments must set `DEBUG=0`, provide a private `SECRET_KEY`, and set the correct `ALLOWED_HOSTS`. Production deployment hardening is handled in later prompts.

To confirm PostgreSQL connectivity without printing the password, run `psql -h 127.0.0.1 -U school_lms -d school_lms -W -c "SELECT current_database(), current_user;"` and enter it at the prompt. Run `migrate` only after confirming the connection points to the local `school_lms` database.

## P005 local demo endpoint

The synthetic learning-goal endpoint is available only when both `DEBUG=1` and the explicit development flag `ENABLE_DEMO_API=1` are set. The sample `.env.example` leaves the flag off. Production (`DEBUG=0`) never registers this route, even if the flag is accidentally enabled. The endpoint has no school or pupil data and does not save submissions.

`GET /api/v1/demo/learning-goal/` returns a sample title and goal with `200`. `POST` accepts JSON with required string fields `title` and `goal`, then returns the validated values with `201`; invalid JSON or missing fields returns `400`. Other methods return `405` for an authenticated request. Global `IsAuthenticated` and session authentication apply, so requests need a signed-in Django session; POST also needs its CSRF token:

```sh
curl -i -b cookies.txt http://127.0.0.1:8000/api/v1/demo/learning-goal/
curl -i -b cookies.txt -H 'Content-Type: application/json' -H 'X-CSRFToken: <csrftoken>' \
  -d '{"title":"Kasrlar","goal":"Umumiy maxrajni topish"}' \
  http://127.0.0.1:8000/api/v1/demo/learning-goal/
```

Run the focused demo tests with `.venv/bin/python manage.py test apps.tests`.

For a persistence check, create one synthetic user, stop and restart Django, then query that same user again:

```sh
.venv/bin/python manage.py shell -c "from accounts.models import User; User.objects.get_or_create(username='p004-persistence-check', defaults={'role': 'pupil'})"
```

After restarting Django, confirm the same row is still present:

```sh
.venv/bin/python manage.py shell -c "from accounts.models import User; print(User.objects.get(username='p004-persistence-check').username)"
```

Start PostgreSQL with `sudo systemctl start postgresql` and stop it with `sudo systemctl stop postgresql`. Start Django with `.venv/bin/python manage.py runserver`; stop the development server with Ctrl+C. Restarting Django does not remove rows from PostgreSQL.
