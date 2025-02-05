from datetime import timedelta
from redis import Redis
from pylock_redis.backend import RedisBackend
import threading
import time

from pylock_redis.lock import Locker


def test_function_is_locked(redis_client: Redis):
    backend = RedisBackend(redis_client)
    locker = Locker(backend, "testidentifier", timedelta(seconds=1), max_retries=5)
    num_runs = 10
    shared_value = do_something(num_runs, locker)
    assert shared_value == num_runs


def do_something(num_runs: int, locker: Locker):
    shared_value = [0]

    def increment():
        with locker:
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
