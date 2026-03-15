from datetime import timedelta
from redis import Redis
from pylock_redis.backend import RedisBackend
import threading
import time
import pytest

from pylock_redis.lock import Locker
from pylock_redis import retry as retry_module


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


def test_reusing_same_locker_can_allow_overlapping_critical_sections(
    redis_client: Redis, monkeypatch: pytest.MonkeyPatch
):
    real_sleep = time.sleep
    monkeypatch.setattr(retry_module.time, "sleep", lambda _: None)
    backend = RedisBackend(redis_client)
    locker = Locker(
        backend,
        "testidentifier",
        timedelta(milliseconds=50),
        max_retries=5,
        backoff_factor=1,
    )
    separate_locker = Locker(
        backend,
        "testidentifier",
        timedelta(milliseconds=50),
        max_retries=1,
        backoff_factor=1,
    )

    # Timeline:
    # 1. first_call enters with the shared Locker and stays alive past the TTL.
    # 2. second_call reuses that same Locker and acquires a new lease.
    # 3. first_call exits late and incorrectly releases second_call's lease.
    # 4. third_call uses a separate Locker and should be blocked until second_call exits.
    #    If third_call enters while second_call is still active, the lock is broken.
    first_call_has_lock = threading.Event()
    second_call_has_lock = threading.Event()
    second_call_is_still_running = threading.Event()
    allow_first_call_to_exit = threading.Event()
    first_call_has_exited = threading.Event()
    overlapping_entry_detected = []

    def first_call():
        with locker:
            first_call_has_lock.set()
            real_sleep(0.06)
            allow_first_call_to_exit.wait(timeout=1)
        first_call_has_exited.set()

    def second_call():
        first_call_has_lock.wait(timeout=1)
        real_sleep(0.06)
        with locker:
            second_call_has_lock.set()
            second_call_is_still_running.set()
            real_sleep(0.2)
            second_call_is_still_running.clear()

    def third_call():
        second_call_has_lock.wait(timeout=1)
        allow_first_call_to_exit.set()
        first_call_has_exited.wait(timeout=1)
        with separate_locker:
            if second_call_is_still_running.is_set():
                overlapping_entry_detected.append(True)

    first_thread = threading.Thread(target=first_call)
    second_thread = threading.Thread(target=second_call)
    third_thread = threading.Thread(target=third_call)

    first_thread.start()
    second_thread.start()
    third_thread.start()

    first_thread.join()
    second_thread.join()
    third_thread.join()

    assert overlapping_entry_detected == []
