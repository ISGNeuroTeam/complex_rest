from django.utils.connection import ConnectionProxy
from django_redis.cache import RedisCache as DjangoRedisCache
from django.core.cache.backends.filebased import FileBasedCache as DjangoFileBasedCache
from django.core.cache.backends.locmem import LocMemCache as DjangoLocMemCache
from django.core.cache.backends.db import DatabaseCache as DjangoDatabaseCache
from django.core.cache.backends.base import InvalidCacheBackendError
from django.core.cache import caches
from django.views.decorators.cache import cache_page
from django.conf import settings
from django.utils.module_loading import import_string


__all__ = ['redis_cache', 'file_cache', 'loc_mem_cache', 'db_cache', 'caches', 'get_cache', 'cache_page']


class RedisCache(DjangoRedisCache):
    pass


class FileCache(DjangoFileBasedCache):
    pass


class LocMemCache(DjangoLocMemCache):
    pass


class DatabaseCache(DjangoDatabaseCache):
    pass


class AuthDatabaseCache(DjangoDatabaseCache):
    """
    Database cache for auth_db
    """
    def __init__(self,  *args, **kwargs):
        """
        Specify app_label for database router
        """
        super().__init__(*args, **kwargs)
        self.cache_model_class._meta.app_label = 'auth'


redis_cache = ConnectionProxy(caches, 'RedisCache')
file_cache = ConnectionProxy(caches, 'FileCache')
loc_mem_cache = ConnectionProxy(caches, 'LocMemCache')
db_cache = ConnectionProxy(caches, 'DatabaseCache')


def get_cache(base_cache, namespace=None, timeout=None, max_entries=None):
    """
    Create or return existing cache instance
    :param base_cache: one of the configured django caches in 'CASHES' settings
    :param namespace: string, only letters, case insensitive,
     namespace for the cache, each key will have prefix with that namespace
    :param timeout: default timeout for cache instance
    :param max_entries: max_entries option for cache instance
    :return:
    cache instance
    """
    if base_cache not in settings.CACHES:
        raise ValueError(f'Cache with name {base_cache} not found CACHES settings')
    if namespace is None:
        return caches[base_cache]

    namespace = namespace.lower()
    cache_name = f'{namespace}_{base_cache}'

    # if cache instance already exists return it
    try:
        cache_instance = caches[cache_name]
        return cache_instance
    except InvalidCacheBackendError:
        pass

    # get base cache params and create new cache instance with timeout and max_entities
    params = settings.CACHES[base_cache].copy()
    backend = params.pop('BACKEND')
    location = params.pop('LOCATION', '')
    try:
        backend_cls = import_string(backend)
    except ImportError as e:
        raise InvalidCacheBackendError(
            "Could not find backend '%s': %s" % (backend, e)
        ) from e
    if timeout is not None:
        params['timeout'] = timeout

    if max_entries is not None:
        params['max_entries'] = max_entries
    params['KEY_PREFIX'] = namespace

    caches[cache_name] = backend_cls(location, params)
    return caches[cache_name]





