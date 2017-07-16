import os
import sys
import redis

from decorators import Monitor
from utils import RetryHandler

class Cache(object):
    def __init__(self, hostname, port, password):
        self._redis = redis.StrictRedis(host=hostname, port=port, db=0, password=password, ssl=True)
        pass

    @Monitor.internal_api()
    def set(self, key, val):
        RetryHandler.retry(lambda: self._redis.set(key, val))

    @Monitor.internal_api()
    def get(self, key):
        return RetryHandler.retry(lambda: self._redis.get(key))

    @Monitor.internal_api()
    def lpush(self, key, val):
        RetryHandler.retry(lambda: self._redis.lpush(key, val))

    @Monitor.internal_api()
    def lpop(self, key):
        return RetryHandler.retry(lambda: self._redis.lpop(key))

    @Monitor.internal_api()
    def llen(self, key):
        return RetryHandler.retry(lambda: self._redis.llen(key))

    @Monitor.internal_api()
    def lrange(self, key, start, end):
        return RetryHandler.retry(lambda: self._redis.lrange(key, start, end))
