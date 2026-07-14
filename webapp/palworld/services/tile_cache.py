from pathlib import Path

from django.conf import settings


class TileCacheError(Exception):
    status_code = 502


class TileNotFound(TileCacheError):
    status_code = 404


def validate_tile(z, x, y):
    if z < 0 or z > settings.PALWORLD_MAP_MAX_ZOOM:
        raise TileNotFound(f'Zoom {z} is outside allowed range')

    max_index = (2**z) - 1
    if x < 0 or y < 0 or x > max_index or y > max_index:
        raise TileNotFound(f'Tile {z}/{x}/{y} is outside allowed range')


def tile_cache_path(z, x, y):
    return Path(settings.PALWORLD_MAP_TILE_CACHE_DIR) / str(z) / str(x) / f'{y}.png'


def tile_missing_path(z, x, y):
    return Path(settings.PALWORLD_MAP_TILE_CACHE_DIR) / str(z) / str(x) / f'{y}.missing'


def get_tile(z, x, y):
    validate_tile(z, x, y)
    path = tile_cache_path(z, x, y)
    if path.exists():
        return path.read_bytes(), True

    if tile_missing_path(z, x, y).exists():
        raise TileNotFound('Tile was previously marked missing')

    raise TileNotFound('Tile is not available in the local cache')
