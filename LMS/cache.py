import redis
from decouple import config
from LMS.settings import REDIS_HOST, REDIS_PORT, REDIS_PASS

class Cache: 
    obj = None
    
    @staticmethod
    def getCacheInstance():
        if Cache.obj is None:
            Cache.obj = redis.Redis(host=REDIS_HOST, port=REDIS_PORT,password=REDIS_PASS)
        return Cache.obj
#  redis configuration