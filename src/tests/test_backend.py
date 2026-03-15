from datetime import timedelta

from pylock_redis.backend import RedisBackend


def test_redis_ping(redis_client):
    backend = RedisBackend(redis_client)
    assert backend.ping()


# AI generated test
def test_unlock_does_not_delete_key_with_wrong_token(redis_client):
    backend = RedisBackend(redis_client)

    assert backend.lock("testidentifier", "token-1", timedelta(seconds=1))
    assert backend.unlock("testidentifier", "token-2") is False
    assert redis_client.get("testidentifier") == b"token-1"

# AI generated test
def test_second_lock_fails_while_first_lock_is_active(redis_client):
    backend = RedisBackend(redis_client)

    assert backend.lock("testidentifier", "token-1", timedelta(seconds=1))
    assert backend.lock("testidentifier", "token-2", timedelta(seconds=1)) is False
