# -*- coding: utf-8 -*-
import time

# Кэш для данных
cache_data = {}
CACHE_TIMEOUTS = {
    'weather': 1800,  # 30 минут
    'search': 300,    # 5 минут
    'stats': 600      # 10 минут
}

def get_cached_data(key):
    """Получить данные из кэша"""
    if key in cache_data:
        data, timestamp = cache_data[key]
        cache_type = key.split('_')[0]
        if time.time() - timestamp < CACHE_TIMEOUTS.get(cache_type, 300):
            print(f"🔧 [CACHE] Использован кэш для: {key}")
            return data
        else:
            del cache_data[key]
            print(f"🔧 [CACHE] Удален устаревший кэш: {key}")
    return None

def set_cached_data(key, data):
    """Сохранить данные в кэш"""
    cache_data[key] = (data, time.time())
    print(f"🔧 [CACHE] Сохранен в кэш: {key}")