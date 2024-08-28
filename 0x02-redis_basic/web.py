#!/usr/bin/env python3
'''A module with tools for request caching and tracking.
'''
import redis
import requests
from functools import wraps
from typing import Callable


redis_store = redis.Redis()
'''The module-level Redis instance.
'''


def data_cacher(method: Callable) -> Callable:
    '''Caches the output of fetched data.
    '''
    @wraps(method)
    def invoker(url) -> str:
        '''The wrapper function for caching the output.
        '''
        redis_store.incr(f'count:{url}')
        result = redis_store.get(f'result:{url}')
        if result:
            return result.decode('utf-8')
        result = method(url)
        redis_store.set(f'count:{url}', 0)
        redis_store.setex(f'result:{url}', 10, result)
        return result
    return invoker


@data_cacher
def get_page(url: str) -> str:
    '''Returns the content of a URL after caching the request's response,
    and tracking the request.
    '''
    return requests.get(url).text

# Bonus: Implement the same functionality using decorators
def cache_with_tracker(expiration: int) -> Callable:
    def decorator(func: Callable) -> Callable:
        def wrapper(url: str) -> str:
            cached_content = redis_store.get(f"cached:{url}")
            if cached_content:
                return cached_content.decode('utf-8')

            content = func(url)

            redis_store.setex(f"cached:{url}", expiration, content)
            redis_store.incr(f"count:{url}")

            return content
        return wrapper
    return decorator

@cache_with_tracker(expiration=10)
def get_page_with_decorator(url: str) -> str:
    """Fetches the content of a URL and caches it for 10 seconds."""
    response = requests.get(url)
    return response.text
