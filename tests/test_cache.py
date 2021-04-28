import time

from django.test import TestCase
from django.conf import settings
from cache import get_cache


class TestCache(TestCase):
    def setUp(self):
        self.base_caches = settings.CACHES

    def _test_timeout(self, base_cache):
        five_cache = get_cache(base_cache, namespace='five', timeout=5)
        ten_cache = get_cache(base_cache, namespace='ten', timeout=10)
        five_cache.set('a', 5)
        ten_cache.set('a', 10)
        a = five_cache.get('a')
        self.assertEqual(a, 5, f'{base_cache}: Value from five second cache has\'nt been retrieved')
        a = ten_cache.get('a')
        self.assertEqual(a, 10, f'{base_cache}: Value from ten second cache has\'nt been retrieved')
        time.sleep(6)
        a = five_cache.get('a')
        self.assertEqual(a, None, f'{base_cache}: Value from five second cache has\'nt been removed by timeout')
        a = ten_cache.get('a')
        self.assertEqual(a, 10, f'{base_cache}: Value from ten second cache has\'nt been retrieved')
        time.sleep(5)
        a = ten_cache.get('a')
        self.assertEqual(a, None, f'{base_cache}: Value from ten second cache has\'nt been removed by timeout')

    def _test_cache_identity(self, base_cache):
        cache1 = get_cache(base_cache, namespace='one')
        cache2 = get_cache(base_cache, namespace='one')
        cache3 = get_cache(base_cache, namespace='two')
        cache4 = get_cache(base_cache, namespace='two')

        self.assertTrue(cache1 is cache2, 'Namespace and base cache must define one cache instance')
        self.assertTrue(cache3 is cache4, 'Namespace and base cache must define one cache instance')
        self.assertFalse(cache2 is cache3, 'Different namespaces  must define different  cache instance')

    def test_timeout(self):
        for base_cache in self.base_caches.keys():
            self._test_timeout(base_cache)

    def test_cache_identity(self):
        for base_cache in self.base_caches.keys():
            self._test_cache_identity(base_cache)

