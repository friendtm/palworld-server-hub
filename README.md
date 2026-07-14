# Palworld Webapp

Django web application for building Palworld server dashboards, admin views, and save-data tooling.

## Current Layout

```text
django-webapp/
  requirements.txt
  webapp/
    manage.py
    palworld/
      data/
        map_points.json
        pal_locations.json
    webapp/
      settings.py
      urls.py
      asgi.py
      wsgi.py
```

## Local Setup

Activate the virtual environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

Copy the example environment file:

```powershell
Copy-Item .env.example .env
```

Run Django from the project directory:

```powershell
cd webapp
python manage.py migrate
python manage.py runserver
```

The local development server will be available at:

```text
http://127.0.0.1:8000/
```

## Palworld Data Sources

Current inputs:

- Palworld REST API for live server info, online players, metrics, and world actor snapshots.
- Local map metadata in `webapp/palworld/data/`.

Keep the Palworld REST API private. The public webapp should use curated data, snapshots, or a private collector instead of exposing Palworld admin endpoints directly.

## Map Assets

The public Django app serves map tiles and icons only from local cache folders:

- `tile-cache/`
- `icon-cache/`
