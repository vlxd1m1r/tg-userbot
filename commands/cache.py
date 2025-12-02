import time

CACHE_TTL = 10  # 10 секунд, можно увеличить
_cache = {}

def cache_get(key):
    if key in _cache:
        value, expire = _cache[key]
        if expire > time.time():
            return value
        del _cache[key]
    return None

def cache_set(key, value, ttl=CACHE_TTL):
    _cache[key] = (value, time.time() + ttl)