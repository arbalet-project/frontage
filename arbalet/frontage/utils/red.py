import redis
import os


def redis_get(attr, default=0):
    v = redis.get(attr)
    if v is None:
        return default
    return v


try:
    redis = redis.StrictRedis(
        host=os.environ['REDIS_HOST'],
        decode_responses=True)
    redis.ping()
except Exception as e:
    raise
