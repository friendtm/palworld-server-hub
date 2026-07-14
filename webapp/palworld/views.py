import json
from pathlib import Path

from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

from .services.api_client import PalworldApiClient
from .services.icon_cache import IconCacheError, get_icon
from .services.tile_cache import TileCacheError, get_tile


MAP_POINTS_PATH = Path(__file__).resolve().parent / 'data' / 'map_points.json'
PAL_LOCATIONS_PATH = Path(__file__).resolve().parent / 'data' / 'pal_locations.json'


def dashboard(request):
    palworld_api = settings.PALWORLD_API.copy()
    palworld_api['PASSWORD_CONFIGURED'] = bool(palworld_api.pop('PASSWORD', ''))

    context = {
        'palworld_api': palworld_api,
        'ingest_configured': bool(settings.PALWORLD_INGEST_TOKEN),
    }
    return render(request, 'palworld/dashboard.html', context)


def map_view(request):
    return render(
        request,
        'palworld/map.html',
        {
            'max_zoom': settings.PALWORLD_MAP_MAX_ZOOM,
        },
    )


def health(request):
    return JsonResponse({'status': 'ok'})


def config(request):
    palworld_api = settings.PALWORLD_API.copy()

    return JsonResponse(
        {
            'debug': settings.DEBUG,
            'allowed_hosts': settings.ALLOWED_HOSTS,
            'palworld_api': {
                'base_url': palworld_api['BASE_URL'],
                'username': palworld_api['USERNAME'],
                'password_configured': bool(palworld_api['PASSWORD']),
                'timeout': palworld_api['TIMEOUT'],
            },
            'ingest_configured': bool(settings.PALWORLD_INGEST_TOKEN),
        }
    )


def palworld_endpoints(request):
    return JsonResponse(
        {
            'endpoints': [
                {'name': 'Server info', 'method': 'GET', 'path': '/info', 'safe': True},
                {'name': 'Players', 'method': 'GET', 'path': '/players', 'safe': True},
                {'name': 'Settings', 'method': 'GET', 'path': '/settings', 'safe': True},
                {'name': 'Metrics', 'method': 'GET', 'path': '/metrics', 'safe': True},
                {'name': 'Game data', 'method': 'GET', 'path': '/game-data', 'safe': True},
                {'name': 'Announce', 'method': 'POST', 'path': '/announce', 'safe': False},
                {'name': 'Save', 'method': 'POST', 'path': '/save', 'safe': False},
                {'name': 'Kick player', 'method': 'POST', 'path': '/kick', 'safe': False},
                {'name': 'Ban player', 'method': 'POST', 'path': '/ban', 'safe': False},
                {'name': 'Shutdown', 'method': 'POST', 'path': '/shutdown', 'safe': False},
                {'name': 'Stop', 'method': 'POST', 'path': '/stop', 'safe': False},
            ]
        }
    )


def palworld_proxy(request, endpoint):
    allowed_endpoints = {
        'info': 'info',
        'players': 'players',
        'settings': 'settings',
        'metrics': 'metrics',
        'game-data': 'game-data',
    }

    path = allowed_endpoints.get(endpoint)
    if path is None:
        return JsonResponse(
            {
                'ok': False,
                'error': 'Unsupported Palworld endpoint',
                'allowed': sorted(allowed_endpoints),
            },
            status=404,
        )

    result = PalworldApiClient().get(path)
    return JsonResponse(result, status=200 if result['ok'] else 502)


def map_tile(request, z, x, y):
    try:
        data, cache_hit = get_tile(z, x, y)
    except TileCacheError as error:
        return JsonResponse(
            {
                'ok': False,
                'error': str(error),
            },
            status=error.status_code,
        )

    response = HttpResponse(data, content_type='image/png')
    response['Cache-Control'] = 'public, max-age=86400'
    response['X-Tile-Cache'] = 'hit' if cache_hit else 'miss'
    return response


def map_points(request):
    data = json.loads(MAP_POINTS_PATH.read_text(encoding='utf-8'))
    for category in data.get('categories', []):
        icon_key = category.get('iconKey', category['key'])
        category['iconUrl'] = f'/map/icons/{icon_key}.png'
    for point in data.get('points', []):
        if point.get('iconKey'):
            point['iconUrl'] = f'/map/icons/{point["iconKey"]}.png'
    return JsonResponse(data)


def pal_locations(request, pal_id):
    data = json.loads(PAL_LOCATIONS_PATH.read_text(encoding='utf-8'))
    pal = data.get('pals', {}).get(pal_id)
    if not pal:
        return JsonResponse(
            {
                'ok': False,
                'error': 'Unknown Pal location layer',
            },
            status=404,
        )

    for point in pal.get('points', []):
        point['iconUrl'] = f'/map/icons/{pal["iconKey"]}.png'

    return JsonResponse({'ok': True, 'pal': pal})


def map_icon(request, icon_key):
    try:
        data, cache_hit, content_type = get_icon(icon_key)
    except IconCacheError as error:
        return JsonResponse(
            {
                'ok': False,
                'error': str(error),
            },
            status=error.status_code,
        )

    response = HttpResponse(data, content_type=content_type)
    response['Cache-Control'] = 'public, max-age=86400'
    response['X-Icon-Cache'] = 'hit' if cache_hit else 'miss'
    return response
