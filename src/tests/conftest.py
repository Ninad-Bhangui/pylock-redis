from redis import Redis
import pytest


@pytest.fixture
def redis_client(request) -> Redis:
    import fakeredis

    return fakeredis.FakeRedis()
