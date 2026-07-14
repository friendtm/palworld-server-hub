# Palworld Server Toolkit

Experimental Django toolkit for Palworld dedicated servers.

This project is being built as a learning/community project. It currently focuses on exposing and visualizing data from the Palworld dedicated server REST API, with early map tooling and local map metadata. It is not a polished production admin panel.

## Current Layout

```text
django-webapp/
  .env.example
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
  tile-cache/
  icon-cache/
```

## Local Setup

Clone the repository, then create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

Copy the example environment file and edit it:

```powershell
Copy-Item .env.example .env
notepad .env
```

Important `.env` values:

```env
DJANGO_SECRET_KEY=change-me
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost

PALWORLD_API_BASE_URL=http://127.0.0.1:8212/v1/api
PALWORLD_API_USERNAME=admin
PALWORLD_API_PASSWORD=your-palworld-admin-password
PALWORLD_API_TIMEOUT=5

PALWORLD_MAP_TILE_CACHE_DIR=tile-cache
PALWORLD_MAP_MAX_ZOOM=6
PALWORLD_MAP_ICON_CACHE_DIR=icon-cache
```

Run Django:

```powershell
cd webapp
python manage.py migrate
python manage.py runserver
```

The local development server will be available at:

```text
http://127.0.0.1:8000/
```

## Palworld REST API Setup

The app expects the Palworld dedicated server REST API to be enabled separately in your server configuration.

The Django app should connect to the Palworld API from a trusted/private network. Do not expose the Palworld REST API directly to the public internet.

The currently used read endpoints are:

- `/info`
- `/players`
- `/settings`
- `/metrics`
- `/game-data`

## Palworld Data Sources

Current inputs:

- Palworld REST API for live server info, online players, metrics, and world actor snapshots.
- Local map metadata in `webapp/palworld/data/`.

Planned inputs:

- Converted `Level.sav` JSON for persisted data such as players, guilds, bases, Pals, containers, and ranking/history features.

Keep the Palworld REST API private. The public webapp should use curated data, snapshots, or a private collector instead of exposing Palworld admin endpoints directly.

## Map Assets

The public Django app serves map tiles and icons only from local cache folders:

- `tile-cache/`
- `icon-cache/`

If the cache folders are empty, map imagery/icons may be missing or fall back to generated placeholder icons.

## Map Assets Notice

Some map tiles and icons are included with this project because the live map feature does not work properly without them.

I do not own these images and do not claim any rights over them. This project is shared for educational and non-commercial purposes only: to show how the code works, how the map is structured, and how others can build similar tools for their own servers.

If any asset owner wants these files removed, I will remove them on request.

## Development Checks

Run these before committing changes:

```powershell
cd webapp
python manage.py check
python manage.py test
```

## Status

This is an early project. Expect rough edges, incomplete features, and implementation changes.

Current focus:

- Django dashboard for Palworld REST API data.
- Live player list and live map integration.
- Local map points/layers.
- Experimental groundwork for future save-file ingestion.
