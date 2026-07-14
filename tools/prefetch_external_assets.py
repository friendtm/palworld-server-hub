import argparse
import json
import time
import urllib.error
import urllib.request
from pathlib import Path


USER_AGENT = 'PalworldDashboardExternalAssetPrefetch/0.1'


def fetch_url(url, timeout):
    request = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        content_type = response.headers.get('Content-Type', '')
        return response.read(), content_type


def write_bytes(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def write_missing_marker(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('404\n', encoding='utf-8')


def prefetch_icons(sources, icon_cache_dir, force, timeout, delay):
    icon_sources = sources.get('iconSources', {})
    fetched = 0
    cached = 0
    failed = 0

    for icon_key, icon_url in sorted(icon_sources.items()):
        path = icon_cache_dir / f'{icon_key}.png'
        if path.exists() and not force:
            cached += 1
            print(f'{icon_key}: cached')
            continue

        try:
            data, content_type = fetch_url(icon_url, timeout)
            if 'image/' not in content_type.lower():
                raise RuntimeError(f'unexpected content type: {content_type}')
            write_bytes(path, data)
        except (OSError, RuntimeError, urllib.error.HTTPError, urllib.error.URLError) as error:
            failed += 1
            print(f'{icon_key}: failed: {error}')
        else:
            fetched += 1
            print(f'{icon_key}: fetched')

        if delay:
            time.sleep(delay)

    return {'icons': len(icon_sources), 'fetched': fetched, 'cached': cached, 'failed': failed}


def prefetch_tiles(sources, tile_cache_dir, min_zoom, max_zoom, force, timeout, delay, progress_every):
    tile_url = sources.get('tileUrl')
    if not tile_url:
        return {'checked': 0, 'fetched': 0, 'cached': 0, 'missing': 0, 'skipped_missing': 0, 'failed': 0}

    checked = 0
    fetched = 0
    cached = 0
    missing = 0
    skipped_missing = 0
    failed = 0
    total = sum((2**z) ** 2 for z in range(min_zoom, max_zoom + 1))

    for z in range(min_zoom, max_zoom + 1):
        max_index = 2**z
        print(f'z{z}: checking {max_index * max_index} tiles')

        for x in range(max_index):
            for y in range(max_index):
                checked += 1
                tile_path = tile_cache_dir / str(z) / str(x) / f'{y}.png'
                missing_path = tile_cache_dir / str(z) / str(x) / f'{y}.missing'

                if tile_path.exists() and not force:
                    cached += 1
                elif missing_path.exists() and not force:
                    skipped_missing += 1
                else:
                    url = tile_url.format(z=z, x=x, y=y)
                    try:
                        data, content_type = fetch_url(url, timeout)
                        if 'image/png' not in content_type.lower():
                            raise RuntimeError(f'unexpected content type: {content_type}')
                        write_bytes(tile_path, data)
                    except urllib.error.HTTPError as error:
                        if error.code == 404:
                            write_missing_marker(missing_path)
                            missing += 1
                        else:
                            failed += 1
                            print(f'{z}/{x}/{y}: failed HTTP {error.code}')
                    except (OSError, RuntimeError, urllib.error.URLError) as error:
                        failed += 1
                        print(f'{z}/{x}/{y}: failed: {error}')
                    else:
                        fetched += 1

                    if delay:
                        time.sleep(delay)

                if checked % progress_every == 0:
                    print(
                        f'checked={checked}/{total} fetched={fetched} cached={cached} '
                        f'missing={missing} skipped_missing={skipped_missing} failed={failed}'
                    )

    return {
        'checked': checked,
        'fetched': fetched,
        'cached': cached,
        'missing': missing,
        'skipped_missing': skipped_missing,
        'failed': failed,
    }


def parse_args():
    parser = argparse.ArgumentParser(description='Prefetch optional external map assets into local cache folders.')
    parser.add_argument('--sources', default='tools/external_asset_sources.local.json')
    parser.add_argument('--tile-cache-dir', default='tile-cache')
    parser.add_argument('--icon-cache-dir', default='icon-cache')
    parser.add_argument('--min-zoom', type=int, default=0)
    parser.add_argument('--max-zoom', type=int, default=6)
    parser.add_argument('--only', choices=['all', 'icons', 'tiles'], default='all')
    parser.add_argument('--force', action='store_true')
    parser.add_argument('--timeout', type=float, default=10)
    parser.add_argument('--delay', type=float, default=0)
    parser.add_argument('--progress-every', type=int, default=250)
    return parser.parse_args()


def main():
    args = parse_args()
    sources_path = Path(args.sources)
    if not sources_path.exists():
        raise SystemExit(f'Sources file not found: {sources_path}')

    sources = json.loads(sources_path.read_text(encoding='utf-8'))
    results = {}

    if args.only in {'all', 'icons'}:
        results['icons'] = prefetch_icons(
            sources,
            Path(args.icon_cache_dir),
            args.force,
            args.timeout,
            args.delay,
        )

    if args.only in {'all', 'tiles'}:
        results['tiles'] = prefetch_tiles(
            sources,
            Path(args.tile_cache_dir),
            max(0, args.min_zoom),
            max(0, args.max_zoom),
            args.force,
            args.timeout,
            args.delay,
            max(1, args.progress_every),
        )

    print(json.dumps(results, indent=2))

    failed = sum(section.get('failed', 0) for section in results.values())
    if failed:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
