from pylock_redis.backend import RedisBackend
import time
import threading


def test_function_is_locked(redis_client):
    backend = RedisBackend(redis_client)
    shared_value = do_something(100)
    assert shared_value == 100


def do_something(num_runs: int):
    shared_value = [0]

    def increment():
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
