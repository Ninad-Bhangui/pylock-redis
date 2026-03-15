from datetime import timedelta
from redis import Redis
from pylock_redis.backend import RedisBackend
import threading
import time
import pytest

from pylock_redis.lock import Locker


def test_function_is_locked(redis_client: Redis):
    backend = RedisBackend(redis_client)
    num_runs = 10
    shared_value = do_something(num_runs, backend)
    assert shared_value == num_runs


def do_something(num_runs: int, backend: RedisBackend):
    shared_value = [0]

    def increment():
        with Locker(backend, "testidentifier", timedelta(seconds=1), max_retries=5):
            current_value = shared_value[0]
            time.sleep(0.0001)
            shared_value[0] = current_value + 1

    threads = []
    for _ in range(num_runs):
        t = threading.Thread(target=increment)
        t.start()
        threads.append(t)

    for t in threads:
        t.join()
    return shared_value[0]


# AI generated test
def test_second_locker_raises_after_retry_limit(redis_client: Redis):
    backend = RedisBackend(redis_client)
    first_locker = Locker(
        backend,
        "testidentifier",
        timedelta(seconds=10),
        max_retries=2,
        backoff_factor=1,
    )
    second_locker = Locker(
        backend,
        "testidentifier",
        timedelta(seconds=10),
        max_retries=1,
        backoff_factor=1,
    )

    with first_locker:
        with pytest.raises(Exception, match="failed after 1 retries"):
            with second_locker:
                pass


def test_reusing_same_locker_raises_runtime_error(redis_client: Redis):
    backend = RedisBackend(redis_client)
    locker = Locker(backend, "testidentifier", timedelta(seconds=1), max_retries=1)

    with locker:
        pass

    with pytest.raises(RuntimeError, match="single use"):
        with locker:
            pass
