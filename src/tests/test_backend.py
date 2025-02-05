from pylock_redis.backend import RedisBackend

def test_redis_ping(redis_client):
    backend = RedisBackend(redis_client)
    assert backend.ping()
