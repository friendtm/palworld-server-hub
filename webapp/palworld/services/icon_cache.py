from pathlib import Path

from django.conf import settings


class IconCacheError(Exception):
    def __init__(self, message, status_code=502):
        super().__init__(message)
        self.status_code = status_code


def _image_content_type(data):
    if data.startswith(b'<svg'):
        return 'image/svg+xml'
    if data.startswith(b'\x89PNG\r\n\x1a\n'):
        return 'image/png'
    if data.startswith(b'\xff\xd8\xff'):
        return 'image/jpeg'
    if data.startswith(b'RIFF') and data[8:12] == b'WEBP':
        return 'image/webp'
    return 'application/octet-stream'


def fallback_icon(icon_key):
    label = (icon_key or '?')[:1].upper()
    colors = {
        'boss': ('#ef6b6b', '#ffe08a'),
        'fast_travel': ('#47d98a', '#edf5f7'),
        'tower': ('#f3bb4b', '#edf5f7'),
        'dungeon': ('#75b7ff', '#edf5f7'),
    }
    fill, stroke = colors.get(icon_key, ('#9fb1b6', '#edf5f7'))
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 48 48">
  <circle cx="24" cy="24" r="18" fill="{fill}" stroke="{stroke}" stroke-width="4"/>
  <text x="24" y="30" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="700" fill="#10181c">{label}</text>
</svg>
'''
    return svg.encode('utf-8')


def get_icon(icon_key):
    cache_dir = settings.PALWORLD_MAP_ICON_CACHE_DIR
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_path = cache_dir / f'{icon_key}.png'
    if cache_path.exists():
        data = cache_path.read_bytes()
        return data, True, _image_content_type(data)

    data = fallback_icon(icon_key)
    return data, False, _image_content_type(data)
