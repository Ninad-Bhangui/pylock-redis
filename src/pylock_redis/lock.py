from collections.abc import Callable
from datetime import timedelta
import functools
import time
from types import TracebackType
from typing import TypeVar
from uuid import uuid4
from .backend import Backend

T = TypeVar("T")

def retry(retries: int, sleep_seconds: int) -> Callable[[Callable[...,T]], Callable[...,T]]:
    def decorator(func: Callable[...,T]) -> Callable[...,T]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            for attempt in range(retries):
                result = func(*args, **kwargs)
                if result:
                    return result
                if attempt < retries - 1:
                    time.sleep(sleep_seconds)

            raise Exception(f"Function {func.__name__} failed after {retries} retries")
        return wrapper
    return decorator


class Locker:
    backend: Backend
    identifier: str
    identifier_value: str
    lock_validity_time: timedelta
    max_retries: int

    def __init__(self, backend: Backend, identifier: str, lock_validity_time: timedelta, max_retries: int) -> None:
        self.backend = backend
        self.identifier = identifier
        self.identifier_value = str(uuid4())
        self.lock_validity_time = lock_validity_time
        self.max_retries = max_retries

    def __enter__(self):
        @retry(self.max_retries, 1)
        def try_lock():
            return self.backend.lock(self.identifier, self.identifier_value, self.lock_validity_time) 
        if try_lock():
            return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType,
    ):
        self.backend.unlock(self.identifier, self.identifier_value)
