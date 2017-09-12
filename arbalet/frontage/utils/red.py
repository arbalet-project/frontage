import redis

def redis_get(attr, default=0):
    v = redis.get(attr)
    if v == None:
        return default
    return v

try:
	redis = redis.StrictRedis(host='redis')
	redis.ping()
except Exception as e:
	raise