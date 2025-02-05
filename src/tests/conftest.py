import pytest

@pytest.fixture
def redis_client(request):
    import fakeredis
    return fakeredis.FakeRedis()

