# Palworld Webapp

Django web application for building Palworld server dashboards, admin views, and save-data tooling.

## Current Layout

```text
django-webapp/
  requirements.txt
  tools/
    external_asset_sources.example.json
    prefetch_external_assets.py
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

Planned inputs:

- Converted `Level.sav` JSON for deeper persisted world data such as players, guilds, bases, Pals, containers, and history.

Keep the Palworld REST API private. The public webapp should use curated data, snapshots, or a private collector instead of exposing Palworld admin endpoints directly.

## Map Assets

The public Django app serves map tiles and icons only from local cache folders:

- `tile-cache/`
- `icon-cache/`

Those folders are ignored by git. The repository should not include third-party map images, icon images, or provider-specific source URLs unless you have explicit permission to redistribute them.

## Optional External Assets

The Django app does not fetch third-party assets at runtime.

For private maintenance, copy `tools/external_asset_sources.example.json` to
`tools/external_asset_sources.local.json`, configure source URLs you are allowed
to use, then run:

```powershell
python tools/prefetch_external_assets.py
```

The local source file and downloaded caches are ignored by git.

## Checks

Run the Django validation suite from `webapp/`:

```powershell
python manage.py check
python manage.py test
```

The tests include a guard that prevents public map data from accidentally including external asset source URLs or old scratch-file references.
