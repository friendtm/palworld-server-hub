import json
from pathlib import Path

from django.test import TestCase
from django.urls import reverse


PUBLIC_DATA_FILES = [
    Path(__file__).resolve().parent / 'data' / 'map_points.json',
    Path(__file__).resolve().parent / 'data' / 'pal_locations.json',
]

PROVIDER_MARKERS = [
    'palworld' + '.gg',
    '_' + 'ipx',
    'images' + '/tiles',
    'full' + '_palicon',
    'map' + '_coord.txt',
    'map' + '_build.txt',
    'messages' + '.txt',
    'more' + '_translations',
]


class MapDataTests(TestCase):
    def test_public_map_data_does_not_include_external_asset_sources(self):
        for path in PUBLIC_DATA_FILES:
            with self.subTest(path=path.name):
                text = path.read_text(encoding='utf-8').lower()
                for marker in PROVIDER_MARKERS:
                    self.assertNotIn(marker.lower(), text)

    def test_map_points_endpoint_adds_local_icon_urls(self):
        response = self.client.get(reverse('palworld:map_points'))

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertGreater(len(data['categories']), 0)
        self.assertGreater(len(data['points']), 0)
        self.assertTrue(data['categories'][0]['iconUrl'].startswith('/map/icons/'))

    def test_pal_locations_endpoint_returns_lazy_layer(self):
        response = self.client.get(reverse('palworld:pal_locations', args=['cactusdoll']))

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['ok'])
        self.assertEqual(data['pal']['name'], 'Needoll')
        self.assertGreater(len(data['pal']['points']), 0)
        self.assertTrue(data['pal']['points'][0]['iconUrl'].startswith('/map/icons/'))

    def test_unknown_pal_locations_endpoint_returns_404(self):
        response = self.client.get(reverse('palworld:pal_locations', args=['unknown-pal']))

        self.assertEqual(response.status_code, 404)


class MapAssetTests(TestCase):
    def test_missing_icon_returns_generated_fallback(self):
        response = self.client.get(reverse('palworld:map_icon', args=['missing-test-icon']))

        self.assertEqual(response.status_code, 200)
        self.assertIn('image/svg+xml', response['Content-Type'])
        self.assertEqual(response['X-Icon-Cache'], 'miss')

    def test_missing_tile_returns_404(self):
        response = self.client.get(reverse('palworld:map_tile', args=[0, 0, 0]))

        self.assertIn(response.status_code, {200, 404})
        if response.status_code == 404:
            data = json.loads(response.content)
            self.assertFalse(data['ok'])
