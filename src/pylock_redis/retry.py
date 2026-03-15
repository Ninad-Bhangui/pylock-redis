from typing import Callable
from typing import TypeVar
import functools
import time
import random


T = TypeVar("T")


def exponential_retry(
    retries: int, backoff_factor: int
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            for attempt in range(retries):
                jitter = random.uniform(0, 1)
                result = func(*args, **kwargs)
                if result:
                    return result
                if attempt < retries - 1:
                    sleep_seconds: float = 1 * (backoff_factor**attempt) + jitter
                    time.sleep(sleep_seconds)

            raise Exception(f"Function {func.__name__} failed after {retries} retries")

        return wrapper

    return decorator
