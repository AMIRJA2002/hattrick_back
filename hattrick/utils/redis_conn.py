from config.env import env
import redis

class RedisConn:
    def __init__(self, host, port, db):
        self.host = host
        self.port = port
        self.db = db
        self.conn = redis.Redis(host=host, port=port, db=db, password=env('REDIS_PASSWORD'), decode_responses=True)

    def get(self, key):
        return self.conn.get(key)

    def set(self, key, value, ttl=None):
        if ttl:
            return self.conn.setex(key, ttl, value)
        return self.conn.set(key, value)

    def delete(self, key):
        return self.conn.delete(key)

    def keys(self, pattern):
        return self.conn.keys(pattern)

    def flushdb(self):
        return self.conn.flushdb()

redis_conn = RedisConn(host=env('REDIS_HOST'), port=env('REDIS_PORT'), db=env('REDIS_DB'))
