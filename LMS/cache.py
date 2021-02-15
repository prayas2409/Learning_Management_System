import redis
from decouple import config

class Cache: 
    obj = None
    
    @staticmethod
    def getCacheInstance():
        if Cache.obj is None:
            Cache.obj = redis.Redis(host=config('REDIS_HOST'), port=config('REDIS_PORT'))
        return Cache.obj
#  redis configuration